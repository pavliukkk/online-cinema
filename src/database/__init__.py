import os

from database.models.base import Base
from database.models.accounts import (
    UserModel,
    UserGroupModel,
    UserGroupEnum,
    ActivationTokenModel,
    PasswordResetTokenModel,
    RefreshTokenModel,
    UserProfileModel
)
from database.models.movies import (
    MovieModel,
    LanguageModel,
    ActorModel,
    GenreModel,
    CountryModel,
    MoviesGenresModel,
    ActorsMoviesModel,
    MoviesLanguagesModel
)
from database.validators import accounts as accounts_validators

environment = os.getenv("ENVIRONMENT", "developing")

from database.session_postgresql import (
    get_postgresql_db_contextmanager as get_db_contextmanager,
    get_postgresql_db as get_db
)
