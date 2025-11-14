import unittest
from unittest.mock import patch, MagicMock
import customtkinter as ctk
import patienteditprofile

class TestPatientEditProfile(unittest.TestCase):

    def setUp(self):
        self.patient_id = 1
        self.patient_fullname = "PATIENT"

        # Patch the database functions and messagebox
        self.patcher_fetch_patient_details = patch('patienteditprofile.fetch_patient_details', return_value=(
            'John Doe', 'john_doe', '123456789012', 'male', '123 Street', '1990-01-01', 'john@example.com', '1234567890'))
        self.patcher_update_patient_details = patch('patienteditprofile.update_patient_details')
        self.patcher_messagebox = patch('patienteditprofile.messagebox')

        self.mock_fetch_patient_details = self.patcher_fetch_patient_details.start()
        self.mock_update_patient_details = self.patcher_update_patient_details.start()
        self.mock_messagebox = self.patcher_messagebox.start()

        # Mock messagebox showinfo to just print the message to simulate the success message
        self.mock_messagebox.showinfo = MagicMock()

        # Create the patient edit profile window
        self.root = ctk.CTk()
        self.app_thread = self.root.after(0, lambda: patienteditprofile.create_patient_edit_profile_window(self.patient_id, self.patient_fullname))
        self.root.mainloop()

    def tearDown(self):
        patch.stopall()
        self.root.destroy()

    def test_confirm_changes(self):
        # Find the confirm button and invoke it
        confirm_button = None
        for widget in self.root.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget('text') == 'Confirm':
                confirm_button = widget
                break

        self.assertIsNotNone(confirm_button, "Confirm button not found")
        confirm_button.invoke()

        # Check if the success message was shown
        self.mock_messagebox.showinfo.assert_called_with("Success", "Profile updated successfully")

if __name__ == '__main__':
    unittest.main()
