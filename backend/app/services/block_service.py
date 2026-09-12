from typing import List, Tuple, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.block import OptimizedBlock

class BlockService:
    @staticmethod
    def get_blocks(db: Session, page: int = 1, page_size: int = 50) -> Tuple[List[OptimizedBlock], int]:
        query = db.query(OptimizedBlock)
        total = query.count()
        blocks = query.options(joinedload(OptimizedBlock.block_tasks)).order_by(OptimizedBlock.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return blocks, total

    @staticmethod
    def get_block_by_id(db: Session, block_id: str) -> Optional[OptimizedBlock]:
        return db.query(OptimizedBlock).options(joinedload(OptimizedBlock.block_tasks)).filter(OptimizedBlock.block_code == block_id).first()

    @staticmethod
    def update_block_status(db: Session, block_id: str, new_status: str) -> Optional[OptimizedBlock]:
        from app.models.block import BlockStatus
        block = db.query(OptimizedBlock).options(joinedload(OptimizedBlock.block_tasks)).filter(OptimizedBlock.block_code == block_id).first()
        if not block:
            return None
        clean_status = new_status.strip().upper()
        if clean_status not in BlockStatus.__members__:
            raise ValueError(f"Invalid status '{new_status}'. Allowed: {list(BlockStatus.__members__.keys())}")
        block.status = BlockStatus[clean_status]
        db.commit()
        db.refresh(block)
        return block

