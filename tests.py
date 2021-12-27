from datetime import datetime

s = "2022-01-02T13:00:00+00:00"
dt = datetime.fromisoformat(s)

# print(dt.year)
# print(dt.month)
# print(dt.day)
# print(dt.hour)
# print(dt.minute)
# print(dt.date())
# print(dt.time())
print(dt.strftime("%m-%d-%y"))
print(dt.strftime("%I:%M %p"))
