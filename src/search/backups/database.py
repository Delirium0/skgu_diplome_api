from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

Base = declarative_base()


class Floor(Base):
    __tablename__ = 'floors'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    image_path = Column(String)
    nodes = relationship("Node", back_populates="floor")


class Node(Base):
    __tablename__ = 'nodes'
    id = Column(String, primary_key=True)
    x = Column(Float)
    y = Column(Float)
    # Дополнительное поле, если нужно хранить тип или другое значение
    extra = Column(String)
    floor_id = Column(Integer, ForeignKey('floors.id'))
    floor = relationship("Floor", back_populates="nodes")
    edges_from = relationship("Edge", back_populates="node_from", foreign_keys='Edge.node_from_id')
    edges_to = relationship("Edge", back_populates="node_to", foreign_keys='Edge.node_to_id')


class Edge(Base):
    __tablename__ = 'edges'
    id = Column(Integer, primary_key=True)
    node_from_id = Column(String, ForeignKey('nodes.id'))
    node_to_id = Column(String, ForeignKey('nodes.id'))
    weight = Column(Float)
    node_from = relationship("Node", foreign_keys=[node_from_id], back_populates="edges_from")
    node_to = relationship("Node", foreign_keys=[node_to_id], back_populates="edges_to")


# Настройка подключения к базе, например, SQLite
engine = create_engine('sqlite:///graph.db')
Session = sessionmaker(bind=engine)
session = Session()

# Если базы ещё нет, создаем её:
Base.metadata.create_all(engine)

# Пример запроса данных:
nodes_data = session.query(Node).all()
edges_data = session.query(Edge).all()
floors_data = session.query(Floor).all()

# Формирование словарей для дальнейшей работы, аналогично загрузке из JSON
nodes = {node.id: (node.x, node.y, node.extra) for node in nodes_data}
floor_mapping = {node.id: node.floor.name for node in nodes_data}
image_paths = {floor.name: floor.image_path for floor in floors_data}
edges = [(edge.node_from_id, edge.node_to_id, edge.weight) for edge in edges_data]

# Далее можно использовать ту же логику построения графа и отрисовки маршрута.
