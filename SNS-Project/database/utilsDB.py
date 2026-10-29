
from database.connection import DatabaseConnection


# ============================================================
#                       Auth Queries
# ============================================================

class AuthQueries:

    @staticmethod
    def checkEmailExists(email: str, data=False):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)

            query = "SELECT * FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()

            cursor.close()
            db_config.close()

            if user:
                if data:
                    return True, user
                return True, "Email already exists"

            return False, "Email does not exist"

        except Exception as e:
            print("Error in checkEmailExists():", e)
            return False, str(e)

    @staticmethod
    def insertUserRecord(username: str, email: str, hash_password: str):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query = """
                INSERT INTO users (username, email, hashpassword)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (username, email, hash_password))
            db_config.commit()

            cursor.close()
            db_config.close()

            return True, "User registered successfully"

        except Exception as e:
            print("Error in insertUserRecord():", e)
            try:
                db_config.rollback()
                cursor.close()
                db_config.close()
            except Exception:
                pass
            return False, str(e)

    @staticmethod
    def updatePassword(email: str, hash_password: str):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query = """
                UPDATE users
                SET hashpassword = %s
                WHERE email = %s
            """
            cursor.execute(query, (hash_password, email))

            if cursor.rowcount == 0:
                db_config.rollback()
                cursor.close()
                db_config.close()
                return False, "User not found or password unchanged"

            db_config.commit()

            cursor.close()
            db_config.close()

            return True, "Password updated successfully"

        except Exception as e:
            print("Error in updatePassword():", e)
            try:
                db_config.rollback()
                cursor.close()
                db_config.close()
            except Exception:
                pass
            return False, str(e)


# ============================================================
#                       Notes Queries
# ============================================================

class NotesQueries:

    @staticmethod
    def insertNotesRecord(userid: int, title: str, content: str):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query = """
                INSERT INTO notes (userid, title, content)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (userid, title, content))
            db_config.commit()

            cursor.close()
            db_config.close()

            return True, "Note added successfully"

        except Exception as e:
            print("Error in insertNotesRecord():", e)
            try:
                db_config.rollback()
                cursor.close()
                db_config.close()
            except Exception:
                pass
            return False, str(e)

    @staticmethod
    def getAllNotes(userid: int, notesid=None):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)

            if notesid is not None:
                query = """
                    SELECT * FROM notes
                    WHERE userid = %s AND notesid = %s
                """
                cursor.execute(query, (userid, notesid))
                notes = cursor.fetchone()
            else:
                query = """
                    SELECT * FROM notes
                    WHERE userid = %s
                    ORDER BY notesid DESC
                """
                cursor.execute(query, (userid,))
                notes = cursor.fetchall()

            cursor.close()
            db_config.close()

            return True, notes

        except Exception as e:
            print("Error in getAllNotes():", e)
            try:
                cursor.close()
                db_config.close()
            except Exception:
                pass
            return False, str(e)

    @staticmethod
    def updateNotes(userid: int, notesid: int, title: str, content: str):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query = """
                UPDATE notes
                SET title = %s, content = %s
                WHERE userid = %s AND notesid = %s
            """
            cursor.execute(query, (title, content, userid, notesid))

            if cursor.rowcount == 0:
                db_config.rollback()
                cursor.close()
                db_config.close()
                return False, "Note not found or no changes made"

            db_config.commit()

            cursor.close()
            db_config.close()

            return True, "Note updated successfully"

        except Exception as e:
            print("Error in updateNotes():", e)
            try:
                db_config.rollback()
                cursor.close()
                db_config.close()
            except Exception:
                pass
            return False, str(e)

    @staticmethod
    def deleteNotes(notesid: int, userid=None):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            if userid is not None:
                query = """
                    DELETE FROM notes
                    WHERE notesid = %s AND userid = %s
                """
                cursor.execute(query, (notesid, userid))
            else:
                query = "DELETE FROM notes WHERE notesid = %s"
                cursor.execute(query, (notesid,))

            if cursor.rowcount == 0:
                db_config.rollback()
                cursor.close()
                db_config.close()
                return False, "Note not found"

            db_config.commit()

            cursor.close()
            db_config.close()

            return True, "Note deleted successfully"

        except Exception as e:
            print("Error in deleteNotes():", e)
            try:
                db_config.rollback()
                cursor.close()
                db_config.close()
            except Exception:
                pass
            return False, str(e)

    @staticmethod
    def getTotalNotes(userid: int):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query = "SELECT COUNT(*) FROM notes WHERE userid = %s"
            cursor.execute(query, (userid,))
            total_notes = cursor.fetchone()[0]

            cursor.close()
            db_config.close()

            return True, total_notes

        except Exception as e:
            print("Error in getTotalNotes():", e)
            try:
                cursor.close()
                db_config.close()
            except Exception:
                pass
            return False, str(e)


# ============================================================
#                       Files Queries
# ============================================================

class FilesQueries:

    @staticmethod
    def insertFileRecord(file_data: tuple):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query = """
                INSERT INTO files
                (userid, originalname, storedname, mimetype, size, filepath)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, file_data)
            db_config.commit()

            cursor.close()
            db_config.close()

            return True, "File uploaded successfully"

        except Exception as e:
            print("Error in insertFileRecord():", e)
            try:
                db_config.rollback()
                cursor.close()
                db_config.close()
            except Exception:
                pass
            return False, str(e)

    @staticmethod
    def getAllFiles(userid: int, fileid=None):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)

            if fileid is not None:
                query = """
                    SELECT * FROM files
                    WHERE userid = %s AND fileid = %s
                """
                cursor.execute(query, (userid, fileid))
                files = cursor.fetchone()
            else:
                query = """
                    SELECT * FROM files
                    WHERE userid = %s
                    ORDER BY fileid DESC
                """
                cursor.execute(query, (userid,))
                files = cursor.fetchall()

            cursor.close()
            db_config.close()

            return True, files

        except Exception as e:
            print("Error in getAllFiles():", e)
            try:
                cursor.close()
                db_config.close()
            except Exception:
                pass
            return False, str(e)

    @staticmethod
    def deleteFile(fileid: int, userid=None):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            if userid is not None:
                query = """
                    DELETE FROM files
                    WHERE fileid = %s AND userid = %s
                """
                cursor.execute(query, (fileid, userid))
            else:
                query = "DELETE FROM files WHERE fileid = %s"
                cursor.execute(query, (fileid,))

            if cursor.rowcount == 0:
                db_config.rollback()
                cursor.close()
                db_config.close()
                return False, "File not found"

            db_config.commit()

            cursor.close()
            db_config.close()

            return True, "File deleted successfully"

        except Exception as e:
            print("Error in deleteFile():", e)
            try:
                db_config.rollback()
                cursor.close()
                db_config.close()
            except Exception:
                pass
            return False, str(e)

    @staticmethod
    def getTotalFiles(userid: int):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query = "SELECT COUNT(*) FROM files WHERE userid = %s"
            cursor.execute(query, (userid,))
            total_files = cursor.fetchone()[0]

            cursor.close()
            db_config.close()

            return True, total_files

        except Exception as e:
            print("Error in getTotalFiles():", e)
            try:
                cursor.close()
                db_config.close()
            except Exception:
                pass
            return False, str(e)
