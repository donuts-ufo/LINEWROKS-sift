import datetime as dt
from sqlalchemy import create_engine, Column, Integer, String, Date, Time, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

engine = create_engine("sqlite:///./shifts.db", echo=False, future=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False, future=True)


class Base(DeclarativeBase):
    pass


class Shift(Base):
    __tablename__ = "shifts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    staff_name: Mapped[str] = mapped_column(String)
    work_date: Mapped[dt.date] = mapped_column(Date)
    start_time: Mapped[dt.time] = mapped_column(Time)
    end_time: Mapped[dt.time] = mapped_column(Time)
    period_tag: Mapped[str] = mapped_column(String)  # 前半 / 後半

    def __repr__(self) -> str:
        return (f"<Shift {self.staff_name} {self.work_date} "
                f"{self.start_time}-{self.end_time}>")

# 初回のみ
def init_db() -> None:
    Base.metadata.create_all(engine)
