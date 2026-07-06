from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Tuple
from csv import DictReader
from io import StringIO
from xml.etree import ElementTree as ET
from app.models.target import Target
from app.schemas.target import TargetCreate
from app.core.exceptions import NotFoundError, ValidationError
from app.utils.logger import logger

class TargetService:
    @staticmethod
    def create_target(db: Session, target: TargetCreate) -> Target:
        db_target = Target(
            engagement_id=target.engagement_id,
            asset_id=target.asset_id,
            host=target.host,
            port=target.port,
            service=target.service,
            protocol=target.protocol,
            auth_type=target.auth_type,
            auth_credentials=target.auth_credentials,
        )
        db.add(db_target)
        db.commit()
        db.refresh(db_target)
        logger.info("target_created", target_id=str(db_target.id), host=target.host)
        return db_target

    @staticmethod
    def get_target(db: Session, target_id: UUID) -> Target:
        target = db.query(Target).filter(Target.id == target_id).first()
        if not target:
            raise NotFoundError(f"Target {target_id} not found")
        return target

    @staticmethod
    def list_targets(db: Session, engagement_id: UUID, skip: int = 0, limit: int = 50) -> Tuple[List[Target], int]:
        query = db.query(Target).filter(Target.engagement_id == engagement_id)
        total = query.count()
        targets = query.offset(skip).limit(limit).all()
        return targets, total

    @staticmethod
    def update_target(db: Session, target_id: UUID, update: dict) -> Target:
        target = TargetService.get_target(db, target_id)
        for field, value in update.items():
            if value is not None:
                setattr(target, field, value)
        db.add(target)
        db.commit()
        db.refresh(target)
        logger.info("target_updated", target_id=str(target_id))
        return target

    @staticmethod
    def delete_target(db: Session, target_id: UUID) -> None:
        target = TargetService.get_target(db, target_id)
        db.delete(target)
        db.commit()
        logger.info("target_deleted", target_id=str(target_id))

    @staticmethod
    def import_csv(db: Session, engagement_id: UUID, csv_content: str) -> Tuple[List[Target], List[str]]:
        targets = []
        errors = []
        try:
            reader = DictReader(StringIO(csv_content))
            for row_num, row in enumerate(reader, start=2):
                try:
                    target = Target(
                        engagement_id=engagement_id,
                        host=row.get("host", "").strip(),
                        port=row.get("port", "").strip() or None,
                        service=row.get("service", "").strip() or None,
                        protocol=row.get("protocol", "").strip() or None,
                    )
                    if not target.host:
                        errors.append(f"Row {row_num}: host is required")
                        continue
                    db.add(target)
                    targets.append(target)
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            db.commit()
            logger.info("targets_imported_csv", engagement_id=str(engagement_id), count=len(targets))
        except Exception as e:
            raise ValidationError(f"CSV import failed: {str(e)}")
        return targets, errors

    @staticmethod
    def import_txt(db: Session, engagement_id: UUID, txt_content: str) -> Tuple[List[Target], List[str]]:
        targets = []
        errors = []
        for line_num, line in enumerate(txt_content.split("\n"), start=1):
            line = line.strip()
            if not line:
                continue
            try:
                target = Target(engagement_id=engagement_id, host=line)
                db.add(target)
                targets.append(target)
            except Exception as e:
                errors.append(f"Line {line_num}: {str(e)}")
        db.commit()
        logger.info("targets_imported_txt", engagement_id=str(engagement_id), count=len(targets))
        return targets, errors

    @staticmethod
    def import_xml(db: Session, engagement_id: UUID, xml_content: str) -> Tuple[List[Target], List[str]]:
        targets = []
        errors = []
        try:
            root = ET.fromstring(xml_content)
            for host_elem in root.findall(".//host"):
                hostnames = host_elem.findall(".//hostnames/hostname")
                ports = host_elem.findall(".//ports/port")
                if hostnames and ports:
                    for port_elem in ports:
                        port_num = port_elem.get("portid", "")
                        for hostname in hostnames:
                            target = Target(
                                engagement_id=engagement_id,
                                host=hostname.text,
                                port=port_num,
                            )
                            db.add(target)
                            targets.append(target)
            db.commit()
            logger.info("targets_imported_xml", engagement_id=str(engagement_id), count=len(targets))
        except ET.ParseError as e:
            raise ValidationError(f"XML parse error: {str(e)}")
        return targets, errors
