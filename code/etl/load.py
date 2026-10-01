from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import pandas as pd
from sqlalchemy import inspect


def create_db_engine(user, password, host, port, database):
    server_url = URL.create(
        drivername="mysql+pymysql",
        username=user,
        password=password,
        host=host,
        port=port,
    )

    server_engine = create_engine(server_url)

    # Create DB if not exists:
    with server_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{database}`"))

    # close server
    server_engine.dispose()

    # access DB:
    db_url = URL.create(
        drivername="mysql+pymysql",
        username=user,
        password=password,
        host=host,
        port=port,
        database=database,
    )

    return create_engine(db_url)


def load_data(df, engine):
    try:
        # ==================================
        # Remove duplicate before loading
        # ==================================

        inspector = inspect(engine)

        if inspector.has_table("jobs"):
            existing = pd.read_sql(
                """SELECT link_description, city, district FROM jobs""", engine
            )
            merged = df.merge(
                existing,
                on=["link_description", "city", "district"],
                how="left",
                indicator=True,
            )
            new_df = merged[merged["_merge"] == "left_only"].drop(columns="_merge")
        else:
            new_df = df

        new_df.to_sql(
            name="jobs", con=engine, if_exists="append", index=False, chunksize=500
        )

        print(f"Loaded {len(new_df)} rows successfully!")

        return new_df

    except Exception as e:
        raise RuntimeError(f"Load failed: {e}")
