import unittest
from unittest.mock import patch, MagicMock
import patient_appointmentsummary

class TestFetchAppointments(unittest.TestCase):

    @patch('patient_appointmentsummary.mysql.connector.connect')
    def test_fetch_appointments_success(self, mock_connect):
        # Setup mock connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        # Define mock return values for past and upcoming appointments
        past_appointments = [
            ('2024-06-16', '10:15:00', 'Eye pain', 'Dr. Smith', 'Clinic A', 'Take rest and use eye drops')
        ]
        upcoming_appointments = [
            ('2024-06-24', '10:30:00', 'General check-up', 'Dr. Doe', 'Clinic B', 'N/A')
        ]

        # Set up the cursor's fetchall() return value
        mock_cursor.fetchall.side_effect = [past_appointments, upcoming_appointments]

        # Call the function to test
        result_past, result_upcoming = patient_appointmentsummary.fetch_appointments(1)

        # Assertions to check if the results match the mock data
        self.assertEqual(result_past, past_appointments)
        self.assertEqual(result_upcoming, upcoming_appointments)

        # Print the data to simulate "seeing" it
        print("Past Appointments:", result_past)
        print("Upcoming Appointments:", result_upcoming)

        # If we reach this point, the test is considered passed
        print("Test Passed")

if __name__ == '__main__':
    unittest.main()
