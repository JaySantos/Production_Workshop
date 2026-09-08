import logging

# logger_a = logging.getLogger("test")
# logger_b = logging.getLogger("test")
# print(logger_a is logger_b)

# logger_c = logging.getLogger("other")
# print(logger_a is logger_c)


class InspectFormatter(logging.Formatter):
    def format(self, record):
        print(record.__dict__)
        if hasattr(record, "context"):
            for x in record.context:
                print(x)
        return super().format(record)


logger = logging.getLogger("test2")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(InspectFormatter())
logger.addHandler(handler)
logger.info("inspecting the record")
# logger.info("inspecting with extra data", extra={"context": {"request_id": "abc-123"}})
