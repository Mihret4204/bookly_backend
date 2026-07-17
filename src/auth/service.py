from src.db.models import User
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from .schemas import UserCreateModel
from .utils import generate_password_hash

class UserService:
    async def get_user_by_email(self,email, session: AsyncSession):
        statement=select(User).where(User.email == email)
        result = await session.execute(statement)
        user= result.scalar_one_or_none()
        return user
    
    async def user_exists(self,email, session:AsyncSession):
        user = await self.get_user_by_email(email,session)

        return  True if user is not None else False
    
    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        
        user_data_dict=user_data.model_dump()

        password = user_data_dict.pop('password')

        password_hash = generate_password_hash(password)

        new_user = User(
            **user_data_dict
        )
        
        new_user.password_hash=password_hash
        new_user.role='admin'
        session.add(new_user)

        await session.commit()

        return new_user
    async def update_user(self, user: User, user_data: dict, session: AsyncSession):

        for k,v in user_data.items():
            setattr(user,k,v)
        
        await session.commit()

        return user