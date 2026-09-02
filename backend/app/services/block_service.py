from typing import List, Tuple, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.block import OptimizedBlock

class BlockService:
    @staticmethod
    def get_blocks(db: Session, page: int = 1, page_size: int = 20) -> Tuple[List[OptimizedBlock], int]:
        query = db.query(OptimizedBlock)
        total = query.count()
        blocks = query.options(joinedload(OptimizedBlock.block_tasks)).order_by(OptimizedBlock.id.asc()).offset((page - 1) * page_size).limit(page_size).all()
        return blocks, total

    @staticmethod
    def get_block_by_id(db: Session, block_id: str) -> Optional[OptimizedBlock]:
        return db.query(OptimizedBlock).options(joinedload(OptimizedBlock.block_tasks)).filter(OptimizedBlock.block_code == block_id).first()
