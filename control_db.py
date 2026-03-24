from extensions import db, bcrypt

participants = db.Table('participants',
                        db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
                        db.Column('meeting_id', db.Integer, db.ForeignKey('meetings.id'), primary_key=True)
                        )


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(70), nullable=False)
    job_title = db.Column(db.String(50), nullable=False)
    user_info = db.Column(db.String(300))
    login = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    profile_picture = db.Column(db.LargeBinary)
    picture_filename = db.Column(db.String(100))

    # Связи
    created_tasks = db.relationship('Task',
                                    foreign_keys='Task.creator_id',
                                    backref='creator',
                                    lazy=True)

    assigned_tasks = db.relationship('Task',
                                     foreign_keys='Task.executor_id',
                                     backref='executor',
                                     lazy=True)

    meetings = db.relationship('Meeting',
                               secondary=participants,
                               back_populates='users')
    # хеширование пароля и проверка пароля
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Meeting(db.Model):
    __tablename__ = 'meetings'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    users = db.relationship('User',
                            secondary=participants,
                            back_populates='meetings')


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    executor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    term = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='new')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
