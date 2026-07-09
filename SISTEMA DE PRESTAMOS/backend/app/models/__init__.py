from flask_sqlalchemy import SQLAlchemy

# 1. Inicializamos la base de datos de forma global
db = SQLAlchemy()

# 2. Importamos todos los modelos DESPUÉS de inicializar 'db'
from .user import User
from .role import Role
from .user_role import UserRole
from .location import Location
from .reservation import Reservation
from .payment import Payment
from .invoice import Invoice
from .review import Review
from .point import Point
from .favorite import Favorite