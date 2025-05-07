from PyQt6 import QtWidgets, uic
import csv
import os
from typing import Dict

class FileManager:
    """Handles reading from and writing to the CSV file with dynamic counters."""

    def __init__(self, filename: str):
        """
        Initialize the FileManager with the given filename.
        Ensures the file exists by calling _ensure_file_exists.
        """
        self._filename = filename
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """
        Ensure the CSV file exists. If it doesn't, create it with the required headers.
        """
        if not os.path.exists(self._filename):
            try:
                with open(self._filename, mode='w', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=["VoterID", "Vote", "Total"])
                    writer.writeheader()
            except IOError as e:
                print(f"Error creating file: {e}")

    def read_data(self) -> Dict[str, int]:
        """
        Read the first row of data from the CSV file.
        Returns a dictionary with the data or default values if the file is empty or unreadable.
        """
        try:
            with open(self._filename, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                return next(reader)
        except (IOError, StopIteration) as e:
            print(f"Error reading file: {e}")
            return {"Jane": 0, "John": 0, "Total": 0}

    def write_data(self, data: Dict[str, int]) -> None:
        """
        Write the given dictionary data to the CSV file, overwriting its contents.
        """
        try:
            with open(self._filename, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=list(data.keys()))
                writer.writeheader()
                writer.writerow(data)
        except IOError as e:
            print(f"Error writing to file: {e}")

    def log_vote(self, voter_id: str, name: str) -> None:
        """
        Log a vote in the CSV file. Each vote includes the voter ID, the name voted for, and the total votes.
        """
        try:
            total_votes = 0
            if os.path.exists(self._filename):
                with open(self._filename, mode='r', newline='') as file:
                    reader = csv.DictReader(file)
                    total_votes = sum(1 for _ in reader if "VoterID" in _)
            total_votes += 1
            with open(self._filename, mode='a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=["VoterID", "Vote", "Total"])
                if file.tell() == 0:
                    writer.writeheader()
                writer.writerow({"VoterID": voter_id, "Vote": name, "Total": total_votes})
        except IOError as e:
            print(f"Error writing to file: {e}")

    def read_results(self) -> Dict[str, int]:
        """
        Read votes from the CSV file and aggregate the results.
        Returns a dictionary with the vote counts and the total number of votes.
        """
        results = {"Jane": 0, "John": 0}
        total_votes = 0
        try:
            with open(self._filename, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if "Jane" in row and "John" in row and "Total" in row and "VoterID" not in row:
                        results["Jane"] = int(row.get("Jane", 0))
                        results["John"] = int(row.get("John", 0))
                        total_votes = int(row.get("Total", 0))
                    elif "Vote" in row:
                        vote = row["Vote"]
                        results[vote] = results.get(vote, 0) + 1
                        total_votes += 1
            results["Total"] = total_votes
        except IOError as e:
            print(f"Error reading file: {e}")
        return results

    def update_count(self, name: str) -> None:
        """
        Increment the vote count for the given name and update the total votes.
        """
        data = self.read_data()
        if name not in data:
            data[name] = 0
        data[name] = int(data.get(name, 0)) + 1
        data["Total"] = int(data.get("Total", 0)) + 1
        self.write_data(data)

    def reset_counts(self) -> None:
        """
        Reset the vote counts in the CSV file by deleting it and recreating it with default values.
        """
        try:
            os.remove('data.csv')
            print(f"File data.csv has been deleted successfully.")
        except Exception as e:
            print(f"Error deleting file: {e}")
        
        self._ensure_file_exists()


class ProjectWindow(QtWidgets.QMainWindow):
    """Main application window for managing the voting system."""

    def __init__(self):
        """
        Initialize the ProjectWindow and set up the UI and button connections.
        """
        super(ProjectWindow, self).__init__()
        uic.loadUi('Project1.ui', self)

        self._file_manager = FileManager('data.csv')

        self.pushButton.clicked.connect(self.on_button_click)
        self.resetButton.clicked.connect(self.reset_votes)
        self.pushButton_2.clicked.connect(self.view_results)

        self.radio_button_group = QtWidgets.QButtonGroup(self)
        self.radio_button_group.addButton(self.johnRadio)
        self.radio_button_group.addButton(self.janeRadio)
        self.radio_button_group.addButton(self.otherRadio)

        self.otherRadio.toggled.connect(self.toggle_textbox_visibility)
        self.lineEdit.hide()
        self.label.setStyleSheet("color: red;")

    def validate_input(self, input_text: str) -> bool:
        """
        Validate that the input text is not empty or just whitespace.
        """
        return bool(input_text.strip())

    def on_button_click(self) -> None:
        """
        Handle the vote submission process, including validation and logging the vote.
        """
        voter_id = self.idInput.text().strip()
        if not self.validate_input(voter_id):
            self.show_error_message("Voter ID is required.")
            return
        try:
            int(voter_id)
        except ValueError:
            self.show_error_message("Voter ID must be a number.")
            return
        
        try:
            with open(self._file_manager._filename, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                headers = reader.fieldnames  # Get headers from the file

                # Check if the required header exists
                if "VoterID" not in headers:
                    self.show_error_message("CSV file is missing the required 'VoterID' column.")
                    return

                # Check if the voter ID already exists
                if any(voter_id == row["VoterID"] for row in reader):  
                    self.show_error_message("This Voter ID has already been used. You cannot vote again.")
                    return
        except IOError:
            self.show_error_message("Error reading file.")
            return

        if self.janeRadio.isChecked():
            self._file_manager.log_vote(voter_id, "Jane")
            self.label.setText("Thank you for voting for Jane!")
        elif self.johnRadio.isChecked():
            self._file_manager.log_vote(voter_id, "John")
            self.label.setText("Thank you for voting for John!")
        elif self.otherRadio.isChecked():
            user_input = self.lineEdit.text().strip()
            if self.validate_input(user_input):
                try:
                    int(user_input)
                    self.show_error_message("Please enter a valid name, not a number.")
                except ValueError:
                    self._file_manager.log_vote(voter_id, user_input)
                    self.label.setText(f"Thank you for voting for {user_input}!")
                    self.lineEdit.clear()
            else:
                self.show_error_message("Invalid input. Please enter non-empty text.")
                return
        else:
            self.show_error_message("Please select an option.")
            return

        self.idInput.clear()

    def toggle_textbox_visibility(self) -> None:
        """
        Show or hide the text box for custom votes based on the "Other" radio button.
        """
        if self.otherRadio.isChecked():
            self.lineEdit.show()
        else:
            self.lineEdit.hide()

    def view_results(self) -> None:
        """
        Display the aggregated voting results in a new window.
        """
        data = self._file_manager.read_results()
        results_window = QtWidgets.QDialog(self)
        results_window.setWindowTitle("Vote Results")
        results_window.resize(400, 300)

        layout = QtWidgets.QVBoxLayout()
        total = data.pop("Total", 0)
        total_label = QtWidgets.QLabel(f"Total Votes: {total}")
        total_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(total_label)

        for name, count in data.items():
            label = QtWidgets.QLabel(f"{name}: {count}")
            label.setStyleSheet("font-size: 14px;")
            layout.addWidget(label)

        results_window.setLayout(layout)
        results_window.exec()

    def reset_votes(self) -> None:
        """
        Reset all votes to zero and update the label to indicate success.
        """
        self._file_manager.reset_counts()
        self.label.setStyleSheet("color: red;")
        self.label.setText("Votes reset successfully!")

    def show_error_message(self, message: str) -> None:
        """
        Display an error message to the user in a message box.
        """
        error_dialog = QtWidgets.QMessageBox(self)
        error_dialog.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("Input Error")
        error_dialog.setText(message)
        error_dialog.setStyleSheet("QLabel { font-size: 14px; }")
        error_dialog.exec()
