package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"github.com/PuerkitoBio/goquery"
	"io"
	"log"
	"net/http"
	"net/http/cookiejar"
	"net/url"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"time"
)

var watchedDepartments = map[int]string{
	// 21: "مهندسی_صنایع",
	// 22: "علوم_ریاضی",
	// 24: "فیزیک",
	// 37: "مرکز_معارف_اسلامی_و_علوم_انسانی",
	40: "مهندسی_کامپیوتر",
}

const BotToken = ""
const ChannelID = ""
const AdminID = ""
const UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
const EduUsername = "99105475"
const EduPassword = "0025148362"

type Course struct {
	ID string
	// Name of the lesson
	Name string
	// Who teaches this course
	Lecturer string
	// Who many students can pick this course at total
	Capacity int
	// How many students has picked this course
	Registered int
	// Units for this course
	Units int
}

func (c *Course) String() string {
	return c.Name + " - " + c.Lecturer + "\nID: " + c.ID + "\nUnits: " + strconv.Itoa(c.Units) + "\nRegistered: " + strconv.Itoa(c.Registered) + "\nCapacity: " + strconv.Itoa(c.Capacity)
}

func (c *Course) StringDiffCapacity(old int) string {
	return c.Name + " - " + c.Lecturer + "\nID: " + c.ID + "\nUnits: " + strconv.Itoa(c.Units) + "\nRegistered: " + strconv.Itoa(c.Registered) + "\nCapacity: " + strconv.Itoa(old) + " → " + strconv.Itoa(c.Capacity)
}

func (c *Course) StringDiffRegistered(old int) string {
	return c.Name + " - " + c.Lecturer + "\nID: " + c.ID + "\nUnits: " + strconv.Itoa(c.Units) + "\nRegistered: " + strconv.Itoa(old) + " → " + strconv.Itoa(c.Registered) + "\nCapacity: " + strconv.Itoa(c.Capacity)
}

type StatusCodeError struct {
	ReceivedStatusCode int
}

func (e StatusCodeError) Error() string {
	return "unexpected status code " + strconv.Itoa(e.ReceivedStatusCode)
}

// IsServerError checks if the server has fucked up
func IsServerError(err error) bool {
	unwrapped, ok := err.(StatusCodeError)
	return ok && unwrapped.ReceivedStatusCode >= 500
}

var Courses = make(map[string]Course)
var httpClient *http.Client
var errorLogin = errors.New("redirected to login page")

func main() {
	// Check startup restore
	if len(os.Args) > 1 {
		file, err := os.Open(os.Args[1])
		if err != nil {
			log.Fatalln("cannot open file:", err)
		}
		err = json.NewDecoder(file).Decode(&Courses)
		if err != nil {
			log.Fatalln("cannot unmarshal json:", err)
		}
		_ = file.Close()
	}
	// Login and retry
	ctx, _ := signal.NotifyContext(context.Background(), os.Interrupt)
	err := Start(ctx)
	if err != nil {
		log.Println("fatal error:", err)
	}
	for errors.Is(err, errorLogin) || IsServerError(err) {
		select {
		case <-time.After(time.Minute):
		case <-ctx.Done():
			return
		}
		log.Println("retrying login")
		continue
	}
	if err == nil {
		if len(Courses) > 0 {
			data, _ := json.Marshal(Courses)
			_ = os.WriteFile("courses-"+strconv.FormatInt(time.Now().Unix(), 10)+".json", data, 0600)
		}
		return
	}
}

func Start(ctx context.Context) (err error) {
	for {
		err = Login(ctx)
		if err == nil {
			break
		} else {
			log.Println("cannot login:", err)
		}
		time.Sleep(time.Second * 10)
	}
	log.Println("login done")
	// for {
	for depID, depName := range watchedDepartments {
		var gotCourses int
		log.Println("getting courses of", depID)
		gotCourses, err = CheckDiff(ctx, depID, depName)
		if err != nil {
			log.Println("cannot get the courses for", depID, err)
			return err
		}
		log.Println("scrapped department", depID, "with", gotCourses, "courses")
		select {
		case <-time.After(time.Second * 5):
		case <-ctx.Done():
			return ctx.Err()
		}
	}
	log.Println("currently have", len(Courses), "courses")
	return nil
}

func CheckDiff(ctx context.Context, departmentID int, departmentName string) (int, error) {
	// Do the request
	resp, err := httpClient.Do(GetRequest(ctx, "POST", "https://edu.sharif.edu/register.do",
		strings.NewReader(url.Values{"level": {"0"}, "teacher_name": {""}, "sort_item": {"1"}, "depID": {strconv.Itoa(departmentID)}}.Encode())))
	if err != nil {
		return 0, err
	}
	defer resp.Body.Close()
	// Check status
	if resp.StatusCode != http.StatusOK {
		return 0, StatusCodeError{resp.StatusCode}
	}
	// Read html
	doc, err := goquery.NewDocumentFromReader(resp.Body)
	if err != nil {
		return 0, err
	}
	// Check login page
	doc.Find("title").Each(func(i int, selection *goquery.Selection) {
		if selection.Text() == "سامانه آموزش - دانشگاه صنعتی شریف" {
			err = errorLogin
		}
	})
	if err != nil {
		return 0, err
	}
	// Get the table
	var coursesGot int
	doc.Find(".contentTable").Each(func(tableI int, table *goquery.Selection) {
		// We only need the first one
		if tableI != 0 {
			return
		}
		// Loop each row
		table.Find("tr").Each(func(_ int, row *goquery.Selection) {
			var course Course
			var ok bool
			row.Find("td").Each(func(i int, column *goquery.Selection) {
				text := strings.Trim(column.Text(), " ")
				// Try to parse the course main ID to see if this is a valid row or not
				if i == 0 {
					_, err := strconv.Atoi(text)
					ok = err == nil
				}
				// If this row is not ok, just return and don't do anything
				if !ok {
					return
				}
				// Now check the index
				switch i {
				case 0: // course ID
					course.ID = text + "-"
				case 1: // course group
					course.ID += text
				case 2: // units
					course.Units, _ = strconv.Atoi(text)
				case 3: // name of course
					course.Name = text
				case 5: // total capacity
					course.Capacity, _ = strconv.Atoi(text)
				case 6:
					course.Registered, _ = strconv.Atoi(text)
				case 7: // Lecturer name
					course.Lecturer = text
				}
			})
			// If we couldn't get this row, just fuck it
			if !ok {
				return
			}
			// Replace the old course
			Courses[course.ID] = course
			coursesGot++
		})
	})
	return coursesGot, nil
}

func Login(ctx context.Context) error {
	jar, _ := cookiejar.New(nil)
	httpClient = &http.Client{
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			return http.ErrUseLastResponse
		},
		Jar: jar,
	}
	resp, err := httpClient.Do(GetRequest(ctx, "GET", "https://edu.sharif.edu/", nil))
	if err != nil {
		return err
	}
	if resp.StatusCode != http.StatusOK {
		_ = resp.Body.Close()
		return StatusCodeError{ReceivedStatusCode: resp.StatusCode}
	}
	// Get body
	_, err = io.ReadAll(resp.Body)
	_ = resp.Body.Close()
	if err != nil {
		return err
	}
	// Login
	req := GetRequest(ctx, "POST", "https://edu.sharif.edu/login.do", strings.NewReader(url.Values{
		"username":         {EduUsername},
		"password":         {EduPassword},
		"jcaptcha":         {"ab"},
		"command":          {"login"},
		"captcha_key_name": {"ab"}, "captchaStatus": {"ab"},
	}.Encode()))
	req.Header.Set("content-type", "application/x-www-form-urlencoded")
	time.Sleep(time.Second)
	resp, err = httpClient.Do(req)
	if err != nil {
		return err
	}
	// Check status code
	body, _ := io.ReadAll(resp.Body)
	_ = resp.Body.Close()
	if !bytes.Contains(body, []byte("خروج")) {
		return errors.New("body is invalid")
	}
	return WarmUp(ctx)
}

func WarmUp(ctx context.Context) error {
	// Open the menu
	resp, err := httpClient.Do(GetRequest(ctx, "POST", "https://edu.sharif.edu/action.do",
		strings.NewReader(url.Values{"changeMenu": {"OnlineRegistration"}, "isShowMenu": {""}, "commandMessage": {""}, "defaultCss": {""}}.Encode())))
	if err != nil {
		return err
	}
	body, _ := io.ReadAll(resp.Body)
	_ = resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return StatusCodeError{resp.StatusCode}
	}
	if IsLogin(body) {
		return errorLogin
	}
	// Change to courses
	resp, err = httpClient.Do(GetRequest(ctx, "POST", "https://edu.sharif.edu/register.do",
		strings.NewReader(url.Values{"changeMenu": {"OnlineRegistration*OfficalLessonListShow"}, "isShowMenu": {""}}.Encode())))
	if err != nil {
		return err
	}
	body, _ = io.ReadAll(resp.Body)
	_ = resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return StatusCodeError{resp.StatusCode}
	}
	if IsLogin(body) {
		return errorLogin
	}
	return nil
}

func GetRequest(ctx context.Context, method, url string, body io.Reader) *http.Request {
	req, _ := http.NewRequest(method, url, body)
	req = req.WithContext(ctx)
	req.Header.Set("user-agent", UserAgent)
	if method == "POST" {
		req.Header.Set("content-type", "application/x-www-form-urlencoded")
	}
	return req
}

func IsLogin(body []byte) bool {
	return bytes.Contains(body, []byte("https://accounts.sharif.edu/cas/login?service=https://edu.sharif.edu/login.jsp"))
}
