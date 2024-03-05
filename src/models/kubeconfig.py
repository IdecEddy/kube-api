from sqlalchemy import Column, Integer, Text
from base import Base

class KubeConfig(Base):
    __tablename__ = 'kubeconfigs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True)  # Assuming one config per user
    config_data = Column(Text, nullable=False)  # Stores the entire kubeconfig file content
