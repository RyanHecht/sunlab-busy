import datetime
import subprocess
import sqlite3



class Session:
    def __init__(self, user, machine, starttime, endtime=None):
        self.user = user
        self.machine = machine
        self.starttime = starttime
        self.endtime = endtime

    def __eq__(self, other):
        return self.user == other.user and self.machine == other.machine and self.starttime == other.starttime

    def __hash__(self):
        return hash((self.user, self.machine, self.starttime))

    def __starttime(self):
        return self.starttime.strftime("%b %d %H:%M")
    def __endtime(self):
        if self.endtime is None:
            return ""
        return self.endtime.strftime("%b %d %H:%M")
    def __str__(self):
        return "User: " + self.user + ", Machine: " + self.machine + ", Starttime: " + self.__starttime()

    def __lt__(self, other):
        return self.starttime < other.starttime

def today_as_rwho_string():
    now = datetime.datetime.now()
    if now.day < 10:
        return now.strftime("%b\\ \\ " + str(now.day))
    else:
        return now.strftime("%b\\ %d")


def get_current_sessions():
    rwho = subprocess.Popen(['rwho', '-a'], stdout=subprocess.PIPE)
    grep = subprocess.Popen(['grep', '-E', 'cslab.*tty.*' + today_as_rwho_string()], stdout=subprocess.PIPE, stdin=rwho.stdout)

    sessions = grep.communicate()[0].decode('utf-8').strip().split("\n")

    current_sessions = []
    for session in sessions:
        splt = session.split()
        if len(splt) > 0:
            name = splt[0]
            machine = splt[1].split(":")[0]
            splt[3] = "0"+splt[3] if int(splt[3]) < 10 else splt[3]
            started = datetime.datetime.strptime(" ".join(splt[2:5]), "%b %d %H:%M")
            started = started.replace(year=datetime.datetime.now().year)
            current_sessions.append(Session(name, machine, started))

    current_sessions.sort()

    for session in current_sessions:
        this_index = current_sessions.index(session)
        if (session.machine in map(lambda s: s.machine, current_sessions[this_index + 1:])):
            current_sessions.remove(session)

    return set(current_sessions)


def process_sessions(sessions):
    conn = sqlite3.connect('/contrib/projects/sunlab-busy/db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("SELECT user, machine, starttime FROM current_sessions")
    known_sessions = set()
    for row in c.fetchall():
        known_sessions.add(Session(str(row[0]), str(row[1]), datetime.datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")))

    for ended_session in known_sessions - sessions:
        c.execute("DELETE FROM current_sessions WHERE user=? AND machine=? AND starttime=?",
        (ended_session.user, ended_session.machine, ended_session.starttime))
        c.execute("INSERT INTO old_sessions (user, machine, starttime, endtime) VALUES (?, ?, ?, ?)",
        (ended_session.user, ended_session.machine, ended_session.starttime, datetime.datetime.now()))
        print("ENDED: " + ended_session.__str__())
    for new_session in sessions - known_sessions:
        c.execute("SELECT * from old_sessions where user=? AND machine=? AND starttime=?", (new_session.user, new_session.machine, new_session.starttime))
        if (len(c.fetchall()) == 0):
            c.execute("INSERT INTO current_sessions (user, machine, starttime) VALUES (?, ?, ?)",
            (new_session.user, new_session.machine, new_session.starttime))
            print("BEGAN: " + new_session.__str__())

    conn.commit()
    conn.close()

#get_current_sessions()
process_sessions(get_current_sessions())
