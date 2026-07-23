from models.links import TransactionTagLink
from models.user import User, UserDefault, UserRegister, UserLogin, UserUpdate
from models.account import Account, AccountDefault
from models.category import Category, CategoryDefault, CategoryType
from models.tag import Tag, TagDefault
from models.budget import Budget, BudgetDefault
from models.transaction import (
    Transaction,
    TransactionDefault,
    TransactionWithCategory,
    TransactionWithTags,
)

User.model_rebuild()
Account.model_rebuild()
Category.model_rebuild()
Tag.model_rebuild()
Budget.model_rebuild()
Transaction.model_rebuild()
