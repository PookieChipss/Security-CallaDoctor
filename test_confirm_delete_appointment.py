import unittest
from unittest.mock import patch, MagicMock
import patienthome
import request_appointment_patient

class TestBookingAndDeletingAppointment(unittest.TestCase):

    @patch('request_appointment_patient.messagebox.showinfo')
    @patch('request_appointment_patient.messagebox.showerror')
    @patch('request_appointment_patient.mysql.connector.connect')
    @patch('request_appointment_patient.root.destroy')
    @patch('patienthome.messagebox.askyesno')
    @patch('patienthome.messagebox.showinfo')
    @patch('patienthome.messagebox.showerror')
    @patch('patienthome.mysql.connector.connect')
    def test_booking_and_deleting_appointment(self, mock_connect_home, mock_showerror_home, mock_showinfo_home, mock_askyesno,
                                              mock_destroy_request, mock_connect_request, mock_showerror_request, mock_showinfo_request):
        # Setup mock connection and cursor for request
        mock_connection_request = MagicMock()
        mock_cursor_request = MagicMock()
        mock_connect_request.return_value = mock_connection_request
        mock_connection_request.cursor.return_value = mock_cursor_request

        # Mock data for clinics and doctors
        request_appointment_patient.clinics = {'Clinic Clash': 130}
        request_appointment_patient.doctor_dict = {'Ruhan': 21}
        request_appointment_patient.patient_id = 1
        request_appointment_patient.patient_fullname = 'Linkesh'

        # Set up the mock return values for booking an appointment
        mock_showinfo_request.return_value = True
        mock_askyesno.return_value = True  # Simulate user clicking "Yes" in the confirmation dialog

        # Define the appointment details
        clinic_name = 'Clinic Clash'
        doctor_name = 'Ruhan'
        reason = 'Eye pain'
        date = '06/24/24'
        hour = '10'
        minute = '30'
        appointment_date = '2024-06-24'

        # Set up the necessary mock returns for booking
        request_appointment_patient.clinic_var = MagicMock()
        request_appointment_patient.doctor_var = MagicMock()
        request_appointment_patient.reason_entry = MagicMock()
        request_appointment_patient.cal = MagicMock()
        request_appointment_patient.hour_var = MagicMock()
        request_appointment_patient.minute_var = MagicMock()

        request_appointment_patient.clinic_var.get.return_value = clinic_name
        request_appointment_patient.doctor_var.get.return_value = doctor_name
        request_appointment_patient.reason_entry.get.return_value = reason
        request_appointment_patient.cal.get_date.return_value = date
        request_appointment_patient.hour_var.get.return_value = hour
        request_appointment_patient.minute_var.get.return_value = minute

        # Call the function to book the appointment
        request_appointment_patient.send_appointment_request()

        # Check that the SQL query was executed correctly for booking
        mock_cursor_request.execute.assert_called_once_with(
            """
            INSERT INTO appointments (clinic_id, doctor_id, patient_id, appointment_date, appointment_time, reason, appointment_request_status)
            VALUES (%s, %s, %s, %s, %s, %s, 'pending')
            """, (130, 21, 1, '2024-06-24', '10:30', 'Eye pain')
        )
        mock_connection_request.commit.assert_called_once()
        mock_cursor_request.close.assert_called_once()
        mock_connection_request.close.assert_called_once()
        mock_showinfo_request.assert_called_once_with("Success", "Appointment request sent successfully!")
        mock_showerror_request.assert_not_called()

        # Setup mock connection and cursor for home
        mock_connection_home = MagicMock()
        mock_cursor_home = MagicMock()
        mock_connect_home.return_value = mock_connection_home
        mock_connection_home.cursor.return_value = mock_cursor_home

        # Define mock return values for past and upcoming appointments
        upcoming_appointments = [
            (appointment_date, '10:30:00', 'Eye pain', 'Ruhan', 'Clinic Clash')
        ]
        mock_cursor_home.fetchall.side_effect = [[], upcoming_appointments]

        # Call the function to fetch appointments
        past_appointments, upcoming_appointments = patienthome.fetch_appointments(1)

        # Assertions to check if the results match the mock data
        self.assertEqual(upcoming_appointments, [
            (appointment_date, '10:30:00', 'Eye pain', 'Ruhan', 'Clinic Clash')
        ])

        # Call the function to delete the appointment
        patienthome.confirm_delete_appointment(appointment_date)

        # Check that the SQL query was executed correctly for deleting
        mock_cursor_home.execute.assert_called_once_with(
            """
            UPDATE appointments
            SET appointment_request_status = 'cancelled'
            WHERE patient_id = %s AND appointment_date = %s
            """, (1, appointment_date)
        )
        mock_connection_home.commit.assert_called_once()
        mock_cursor_home.close.assert_called_once()
        mock_connection_home.close.assert_called_once()
        mock_showinfo_home.assert_called_once_with("Success", "Appointment request cancelled successfully!")
        mock_showerror_home.assert_not_called()

        # Print "Test Passed" to indicate the test passed
        print("Test Passed")

if __name__ == '__main__':
    unittest.main()
