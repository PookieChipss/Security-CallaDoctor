import unittest
from unittest.mock import patch, MagicMock
import request_appointment_patient

class TestSendAppointmentRequest(unittest.TestCase):

    @patch('request_appointment_patient.messagebox.showinfo')
    @patch('request_appointment_patient.messagebox.showerror')
    @patch('request_appointment_patient.mysql.connector.connect')
    def test_send_appointment_request_success(self, mock_connect, mock_showerror, mock_showinfo):
        # Mock the Tkinter variables
        request_appointment_patient.clinic_var = MagicMock()
        request_appointment_patient.doctor_var = MagicMock()
        request_appointment_patient.reason_entry = MagicMock()
        request_appointment_patient.cal = MagicMock()
        request_appointment_patient.hour_var = MagicMock()
        request_appointment_patient.minute_var = MagicMock()

        # Set up the mock return values
        request_appointment_patient.clinic_var.get.return_value = 'Clinic Clash'
        request_appointment_patient.doctor_var.get.return_value = 'Ruhan'
        request_appointment_patient.reason_entry.get.return_value = 'Eye pain'
        request_appointment_patient.cal.get_date.return_value = '06/24/24'
        request_appointment_patient.hour_var.get.return_value = '10'
        request_appointment_patient.minute_var.get.return_value = '30'

        # Mock data for clinics and doctors
        request_appointment_patient.clinics = {'Clinic Clash': 130}
        request_appointment_patient.doctor_dict = {'Ruhan': 21}
        request_appointment_patient.patient_id = 1
        request_appointment_patient.patient_fullname = 'Linkesh'

        # Setup mock connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        # Call the function to test
        request_appointment_patient.send_appointment_request()

        # Check that database insert was called correctly
        mock_cursor.execute.assert_called_once_with(
            """
            INSERT INTO appointments (clinic_id, doctor_id, patient_id, appointment_date, appointment_time, reason, appointment_request_status)
            VALUES (%s, %s, %s, %s, %s, %s, 'pending')
            """, (130, 21, 1, '2024-06-24', '10:30', 'Eye pain')
        )
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()
        mock_showinfo.assert_called_once_with("Success", "Appointment request sent successfully!")
        mock_showerror.assert_not_called()

    @patch('request_appointment_patient.messagebox.showinfo')
    @patch('request_appointment_patient.messagebox.showerror')
    def test_send_appointment_request_missing_clinic(self, mock_showerror, mock_showinfo):
        # Mock the Tkinter variables
        request_appointment_patient.clinic_var = MagicMock()
        request_appointment_patient.doctor_var = MagicMock()
        request_appointment_patient.reason_entry = MagicMock()
        request_appointment_patient.cal = MagicMock()
        request_appointment_patient.hour_var = MagicMock()
        request_appointment_patient.minute_var = MagicMock()

        # Set up the mock return values
        request_appointment_patient.clinic_var.get.return_value = ''
        request_appointment_patient.doctor_var.get.return_value = 'Ruhan'
        request_appointment_patient.reason_entry.get.return_value = 'Eye pain'
        request_appointment_patient.cal.get_date.return_value = '06/24/24'
        request_appointment_patient.hour_var.get.return_value = '10'
        request_appointment_patient.minute_var.get.return_value = '30'

        # Mock data for clinics and doctors
        request_appointment_patient.clinics = {'Clinic Clash': 130}
        request_appointment_patient.doctor_dict = {'Ruhan': 21}
        request_appointment_patient.patient_id = 1
        request_appointment_patient.patient_fullname = 'Linkesh'

        # Call the function to test
        request_appointment_patient.send_appointment_request()

        # Check that error message was shown
        mock_showerror.assert_called_once_with("Error", "Please select a clinic.")
        mock_showinfo.assert_not_called()

if __name__ == '__main__':
    unittest.main()
