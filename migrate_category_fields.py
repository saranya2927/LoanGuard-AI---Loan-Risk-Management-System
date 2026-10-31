
from sqlalchemy import inspect, text

from app.database import engine


# Columns required by the current Application model
REQUIRED_COLUMNS = {
    "startup_name": "VARCHAR",
    "startup_business_stage": "VARCHAR",
    "startup_business_age_years": "FLOAT",
    "startup_annual_revenue": "FLOAT",
    "startup_funding_required": "FLOAT",
    "startup_existing_funding": "FLOAT",

    "investor_investment_experience": "VARCHAR",
    "investor_annual_investment_income": "FLOAT",
    "investor_investment_portfolio_value": "FLOAT",
    "investor_investment_purpose": "VARCHAR",

    "occupation": "VARCHAR",
    "residential_status": "VARCHAR",
}


def migrate_database():

    inspector = inspect(engine)

    if not inspector.has_table("applications"):
        print("ERROR: Applications table does not exist.")
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("applications")
    }

    added_columns = []

    with engine.begin() as connection:

        for column_name, column_type in REQUIRED_COLUMNS.items():

            if column_name not in existing_columns:

                sql = (
                    f"ALTER TABLE applications "
                    f"ADD COLUMN {column_name} {column_type}"
                )

                connection.execute(text(sql))

                added_columns.append(column_name)

                print(f"Added column: {column_name}")

    if added_columns:
        print("\nDatabase migration completed successfully.")
    else:
        print("\nAll required columns already exist.")

    print("\nVerified application columns:")

    updated_inspector = inspect(engine)

    for column in updated_inspector.get_columns("applications"):
        if column["name"] in REQUIRED_COLUMNS:
            print(" -", column["name"])


if __name__ == "__main__":
    migrate_database()
