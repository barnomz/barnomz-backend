from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from forms import LoginForm
from rest_framework import generics
from models import User


