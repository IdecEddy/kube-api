from sqlalchemy import Column, Integer, Text
from models.base import Base

class KubeConfig(Base):
    __tablename__ = 'kubeconfigs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)  # Assuming one config per user
    config_data = Column(Text, nullable=False)  # Stores the entire kubeconfig file content