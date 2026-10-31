
import sqlite3
from pathlib import Path


# Database path
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "loanguard.db"


# New student-related database columns
NEW_COLUMNS = {
    "student_institution_name": "VARCHAR",
    "student_course": "VARCHAR",
    "student_year_of_study": "INTEGER",
    "student_expected_graduation": "INTEGER",
    "student_education_loan_requirement": "VARCHAR",

    "student_support_source": "VARCHAR",
    "student_guardian_relationship": "VARCHAR",
    "student_guardian_occupation": "VARCHAR",
    "student_guardian_monthly_income": "FLOAT",
    "student_scholarship_amount": "FLOAT",
    "student_co_applicant_available": "BOOLEAN",
    "student_co_applicant_relationship": "VARCHAR",
}


def migrate_database():

    if not DATABASE_PATH.exists():
        print("ERROR: Database file not found!")
        print(f"Expected location: {DATABASE_PATH}")
        return

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = connection.cursor()

        # Check whether applications table exists
        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table' AND name='applications'
        """)

        if cursor.fetchone() is None:
            print("ERROR: Applications table not found!")
            return

        # Read existing columns
        cursor.execute("PRAGMA table_info(applications)")

        existing_columns = {
            row[1] for row in cursor.fetchall()
        }

        added_count = 0

        print("\nStarting student database migration...\n")

        for column_name, column_type in NEW_COLUMNS.items():

            if column_name not in existing_columns:

                query = (
                    f"ALTER TABLE applications "
                    f"ADD COLUMN {column_name} {column_type}"
                )

                cursor.execute(query)

                print(f"ADDED: {column_name}")

                added_count += 1

            else:
                print(f"ALREADY EXISTS: {column_name}")

        connection.commit()

        print("\n--------------------------------")
        print("DATABASE MIGRATION COMPLETED")
        print("--------------------------------")
        print(f"New columns added: {added_count}")
        print(f"Database: {DATABASE_PATH}")

    except Exception as error:

        connection.rollback()

        print("\nMIGRATION FAILED!")
        print(f"Reason: {error}")

    finally:
        connection.close()


if __name__ == "__main__":
    migrate_database()
