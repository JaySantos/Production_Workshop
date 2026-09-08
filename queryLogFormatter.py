import json
import logging


class QueryLogFormatter(logging.Formatter):
    def format(self, record):
        output = {}
        output["filename"] = record.filename
        output["lineno"] = record.lineno
        output["created"] = record.created
        output["readable_created"] = self.formatTime(record)
        output["levelname"] = record.levelname
        output["message"] = record.getMessage()
        if hasattr(record, "context"):
            for key in record.context:
                output[key] = record.context[key]
        return json.dumps(output)
