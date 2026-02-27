import pytest
import uuid
from httpx import ASGITransport, AsyncClient
from backend.main import app
from datetime import datetime, date

BASE_URL = "http://testserver"
