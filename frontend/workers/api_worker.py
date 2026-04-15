from PyQt6.QtCore import QThread, pyqtSignal
from frontend.core.api_client import ApiClient

class ApiWorker(QThread):
    data_fetched = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, action: str, **kwargs):
        super().__init__()
        self.action = action
        self.kwargs = kwargs
        self.setTerminationEnabled(True)

    def run(self):
        try:
            data = ApiClient.get_all(self.action)

            if self.isInterruptionRequested():
                return

            if isinstance(data, list):
                self.data_fetched.emit(data)
            elif isinstance(data, dict):
                self.data_fetched.emit([data])
            else:
                self.data_fetched.emit([])

        except Exception as e:
            if not self.isInterruptionRequested():
                self.error_occurred.emit(str(e))