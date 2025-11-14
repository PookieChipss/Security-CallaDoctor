import unittest
from unittest.mock import patch, MagicMock
import main_page

class TestOpenForgotPasswordPage(unittest.TestCase):

    @patch('main_page.subprocess.run')
    @patch('main_page.ctk.CTk.destroy')
    def test_open_forgot_password_page(self, mock_destroy, mock_subprocess_run):
        # Set up the global login_root as a MagicMock instance
        main_page.login_root = MagicMock()

        # Call the function to test
        main_page.open_forgot_password_page()

        # Check that the login_root.destroy method was called
        main_page.login_root.destroy.assert_called_once()

        # Check that the subprocess.run method was called with the correct arguments
        mock_subprocess_run.assert_called_once_with(['python', 'forgot_password.py'])

        # Print "Test Passed" to indicate the test passed
        print("Test Passed")

if __name__ == '__main__':
    unittest.main()
