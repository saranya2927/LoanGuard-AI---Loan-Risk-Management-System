
from sqlalchemy import inspect, text

from app.database import engine


def migrate_database():
    inspector = inspect(engine)

    if "applications" not in inspector.get_table_names():
        print("Applications table not found.")
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("applications")
    }

    with engine.begin() as connection:

        if "applicant_type" not in existing_columns:
            connection.execute(
                text(
                    "ALTER TABLE applications "
                    "ADD COLUMN applicant_type VARCHAR "
                    "NOT NULL DEFAULT 'Individual'"
                )
            )
            print("Added applicant_type column.")
        else:
            print("applicant_type column already exists.")

        if "recommendations" not in existing_columns:
            connection.execute(
                text(
                    "ALTER TABLE applications "
                    "ADD COLUMN recommendations JSON"
                )
            )
            print("Added recommendations column.")
        else:
            print("recommendations column already exists.")

    print("\nDatabase migration completed successfully!")


if __name__ == "__main__":
    migrate_database()
