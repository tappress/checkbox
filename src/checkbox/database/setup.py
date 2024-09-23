from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine


def create_sa_engine(postgres_url: str, **kwargs) -> AsyncEngine:
    return create_async_engine(postgres_url, **kwargs)


def create_sa_sessionmaker(engine: AsyncEngine) -> async_sessionmaker:
    # We set `expire_on_commit=False` because we don't want to use `await session.refresh(model)`
    # for each newly created model. Without `expire_on_commit=False` or refreshing,
    # we will get the following error after committing and trying to access model's attributes:
    # ---
    # Error extracting attribute: MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here.
    # ---
    # This is because after expiring and object, on attribute/object access, SQLAlchemy will try to load
    # the most recent database state and "await" cannot be used when accessing object attributes: model.some_attribute
    return async_sessionmaker(engine, expire_on_commit=False)
