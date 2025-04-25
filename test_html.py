from flask import Flask, render_template, request, jsonify
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
import sys
import threading

app = Flask(__name__, template_folder="templates")