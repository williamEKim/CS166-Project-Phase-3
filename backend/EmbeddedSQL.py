import sys
import psycopg2

class EmbeddedSQL:
    """
    A simple embedded SQL utility class designed to work with PostgreSQL
    via the psycopg2 driver.
    """

    def __init__(self, dbname, dbport, user, passwd=""):
        """
        Creates a new instance of EmbeddedSQL and establishes a physical
        connection to the database.

        :param dbname:  the name of the database
        :param dbport:  the port the PostgreSQL server is running on
        :param user:    the user name used to login to the database
        :param passwd:  the user login password
        """
        print("Connecting to database...")
        try:
            self._connection = psycopg2.connect(
                database=dbname,
                user=user,
                password=passwd,
                host="localhost",
                port=dbport
            )
            print(f"Connection URL: postgresql://localhost:{dbport}/{dbname}\n")
            print("Done")
        except Exception as e:
            print(f"Error - Unable to Connect to Database: {e}", file=sys.stderr)
            print("Make sure you started postgres on this machine")
            sys.exit(-1)

    def execute_update(self, sql, params=None):
        """
        Executes an update SQL statement (CREATE, INSERT, UPDATE, DELETE, DROP).

        :param sql: the input SQL string
        :param params: optional tuple of parameters for parameterized queries
        """
        cursor = self._connection.cursor()

        try:
            cursor.execute(sql, params)
            self._connection.commit()
            return True
        except Exception as e:
            self._connection.rollback()
            print(f"Error executing update: {e}")
            return False
        finally:
            cursor.close()

    def execute_query(self, query, params=None):
        """
        Executes a SELECT query and prints the results in a cleaner table format.
        """
        cursor = self._connection.cursor()

        try:
            cursor.execute(query, params)

            col_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            if not rows:
                print("No results found.")
                return 0

            clean_rows = []
            for row in rows:
                clean_row = []
                for val in row:
                    if val is None:
                        clean_row.append("")
                    else:
                        clean_row.append(str(val).strip())
                clean_rows.append(clean_row)

            widths = []
            for i, col_name in enumerate(col_names):
                max_width = len(col_name)

                for row in clean_rows:
                    max_width = max(max_width, len(row[i]))

                widths.append(max_width)

            header = " | ".join(col_names[i].ljust(widths[i]) for i in range(len(col_names)))
            separator = "-+-".join("-" * widths[i] for i in range(len(col_names)))

            print(header)
            print(separator)

            for row in clean_rows:
                print(" | ".join(row[i].ljust(widths[i]) for i in range(len(row))))

            return len(rows)

        except Exception as e:
            print("Error:", e)
            return 0

        finally:
            cursor.close()
            

    def execute_transaction(self, statements):
        """
        Executes a list of SQL statements as a single transaction.

        :param statements: a list of tuples (sql, params) where sql is the SQL string
                           and params is an optional tuple of parameters for parameterized queries
        """
        cursor = self._connection.cursor()

        try:
            for sql, params in statements:
                cursor.execute(sql, params)
            self._connection.commit()
            return True
        except Exception as e:
            self._connection.rollback()
            print(f"Error executing transaction: {e}")
            return False
        finally:
            cursor.close()

    def fetch_one(self, query, params=None):
        cursor = self._connection.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        return result

    def fetch_all(self, query, params=None):
        cursor = self._connection.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        return results

    def cursor(self):
        return self._connection.cursor()

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def cleanup(self):
        """
        Closes the physical connection if it is open.
        """
        try:
            if self._connection is not None:
                self._connection.close()
        except Exception:
            pass  # ignored
