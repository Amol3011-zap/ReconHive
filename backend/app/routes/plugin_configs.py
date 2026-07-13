"""Plugin Configuration API Routes"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.plugins.config_manager import PluginConfigurationManager
from app.models.plugin_config import ConfigStatus
from app.core.exceptions import NotFoundError, ValidationError, ConflictError
from app.utils.logger import logger


# Pydantic schemas
class ConfigSettingsSchema(BaseModel):
    """Configuration settings"""
    class Config:
        json_schema_extra = {
            "example": {
                "timeout": 300,
                "retries": 3,
                "verbose": True,
                "excluded_paths": ["/admin", "/api/internal"],
            }
        }


class PluginConfigurationCreate(BaseModel):
    """Create new configuration"""
    name: str = Field(..., description="Configuration name (e.g., 'default', 'aggressive')")
    description: Optional[str] = None
    settings: dict = Field(default={}, description="Configuration settings")
    is_default: bool = Field(default=False, description="Set as default configuration")


class PluginConfigurationUpdate(BaseModel):
    """Update configuration"""
    settings: Optional[dict] = None
    env_vars: Optional[dict] = None
    description: Optional[str] = None
    reason: Optional[str] = Field(None, description="Reason for update")


class PluginConfigurationResponse(BaseModel):
    """Configuration response model"""
    id: str
    plugin_id: str
    name: str
    description: Optional[str]
    version: str
    settings: dict
    env_vars: dict
    status: str
    is_default: bool
    is_validated: bool
    validation_errors: List[str]
    created_by: Optional[str]
    created_at: str
    updated_at: str
    activated_at: Optional[str]
    last_used_at: Optional[str]
    use_count: str

    class Config:
        from_attributes = True


class ConfigurationHistoryResponse(BaseModel):
    """Configuration history entry"""
    id: str
    config_id: str
    action: str
    changed_by: Optional[str]
    old_settings: Optional[dict]
    new_settings: Optional[dict]
    reason: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class ConfigurationListResponse(BaseModel):
    """List of configurations with pagination"""
    configurations: List[PluginConfigurationResponse]
    total: int
    skip: int
    limit: int


class ConfigurationHistoryListResponse(BaseModel):
    """List of history entries"""
    history: List[ConfigurationHistoryResponse]
    total: int
    skip: int
    limit: int


router = APIRouter(prefix="/plugins/{plugin_id}/configs", tags=["Plugin Configurations"])


@router.post("", response_model=PluginConfigurationResponse, status_code=201)
def create_configuration(
    plugin_id: UUID,
    config: PluginConfigurationCreate,
    db: Session = Depends(get_db),
    current_user: str = Query("system"),
):
    """Create a new configuration for a plugin"""
    try:
        new_config = PluginConfigurationManager.create_configuration(
            db=db,
            plugin_id=plugin_id,
            name=config.name,
            settings=config.settings,
            description=config.description,
            created_by=current_user,
            is_default=config.is_default,
        )
        return new_config
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("create_config_error", error=str(e), plugin_id=str(plugin_id))
        raise HTTPException(status_code=500, detail="Failed to create configuration")


@router.get("", response_model=ConfigurationListResponse)
def list_configurations(
    plugin_id: UUID,
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all configurations for a plugin"""
    try:
        status_enum = ConfigStatus(status) if status else None
        configs, total = PluginConfigurationManager.list_configurations(
            db=db,
            plugin_id=plugin_id,
            status=status_enum,
            skip=skip,
            limit=limit,
        )
        return ConfigurationListResponse(
            configurations=configs,
            total=total,
            skip=skip,
            limit=limit,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("list_configs_error", error=str(e), plugin_id=str(plugin_id))
        raise HTTPException(status_code=500, detail="Failed to list configurations")


@router.get("/default")
def get_default_configuration(
    plugin_id: UUID,
    db: Session = Depends(get_db),
):
    """Get the active (default) configuration for a plugin"""
    try:
        config = PluginConfigurationManager.get_active_configuration(db=db, plugin_id=plugin_id)
        if not config:
            raise HTTPException(status_code=404, detail="No active configuration for this plugin")
        return config
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_default_config_error", error=str(e), plugin_id=str(plugin_id))
        raise HTTPException(status_code=500, detail="Failed to get default configuration")


@router.get("/{config_id}", response_model=PluginConfigurationResponse)
def get_configuration(
    plugin_id: UUID,
    config_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a specific configuration"""
    try:
        config = PluginConfigurationManager.get_configuration(db=db, config_id=config_id)
        if config.plugin_id != plugin_id:
            raise HTTPException(status_code=404, detail="Configuration not found for this plugin")
        return config
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("get_config_error", error=str(e), config_id=str(config_id))
        raise HTTPException(status_code=500, detail="Failed to get configuration")


@router.put("/{config_id}", response_model=PluginConfigurationResponse)
def update_configuration(
    plugin_id: UUID,
    config_id: UUID,
    update: PluginConfigurationUpdate,
    db: Session = Depends(get_db),
    current_user: str = Query("system"),
):
    """Update a configuration"""
    try:
        config = PluginConfigurationManager.get_configuration(db=db, config_id=config_id)
        if config.plugin_id != plugin_id:
            raise HTTPException(status_code=404, detail="Configuration not found for this plugin")

        updated_config = PluginConfigurationManager.update_configuration(
            db=db,
            config_id=config_id,
            settings=update.settings,
            env_vars=update.env_vars,
            description=update.description,
            updated_by=current_user,
            reason=update.reason,
        )
        return updated_config
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("update_config_error", error=str(e), config_id=str(config_id))
        raise HTTPException(status_code=500, detail="Failed to update configuration")


@router.post("/{config_id}/validate")
def validate_configuration(
    plugin_id: UUID,
    config_id: UUID,
    db: Session = Depends(get_db),
):
    """Validate a configuration against plugin schema"""
    try:
        config = PluginConfigurationManager.get_configuration(db=db, config_id=config_id)
        if config.plugin_id != plugin_id:
            raise HTTPException(status_code=404, detail="Configuration not found for this plugin")

        is_valid, errors = PluginConfigurationManager.validate_configuration(db=db, config_id=config_id)
        return {
            "config_id": str(config_id),
            "is_valid": is_valid,
            "errors": errors,
        }
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("validate_config_error", error=str(e), config_id=str(config_id))
        raise HTTPException(status_code=500, detail="Failed to validate configuration")


@router.post("/{config_id}/activate")
def activate_configuration(
    plugin_id: UUID,
    config_id: UUID,
    db: Session = Depends(get_db),
    current_user: str = Query("system"),
):
    """Activate a configuration (make it the default)"""
    try:
        config = PluginConfigurationManager.get_configuration(db=db, config_id=config_id)
        if config.plugin_id != plugin_id:
            raise HTTPException(status_code=404, detail="Configuration not found for this plugin")

        activated_config = PluginConfigurationManager.activate_configuration(
            db=db,
            config_id=config_id,
            activated_by=current_user,
        )
        return activated_config
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("activate_config_error", error=str(e), config_id=str(config_id))
        raise HTTPException(status_code=500, detail="Failed to activate configuration")


@router.post("/{config_id}/deactivate")
def deactivate_configuration(
    plugin_id: UUID,
    config_id: UUID,
    db: Session = Depends(get_db),
    current_user: str = Query("system"),
):
    """Deactivate a configuration"""
    try:
        config = PluginConfigurationManager.get_configuration(db=db, config_id=config_id)
        if config.plugin_id != plugin_id:
            raise HTTPException(status_code=404, detail="Configuration not found for this plugin")

        deactivated_config = PluginConfigurationManager.deactivate_configuration(
            db=db,
            config_id=config_id,
            deactivated_by=current_user,
        )
        return deactivated_config
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("deactivate_config_error", error=str(e), config_id=str(config_id))
        raise HTTPException(status_code=500, detail="Failed to deactivate configuration")


@router.delete("/{config_id}", status_code=204)
def delete_configuration(
    plugin_id: UUID,
    config_id: UUID,
    db: Session = Depends(get_db),
    current_user: str = Query("system"),
):
    """Archive a configuration (soft delete)"""
    try:
        config = PluginConfigurationManager.get_configuration(db=db, config_id=config_id)
        if config.plugin_id != plugin_id:
            raise HTTPException(status_code=404, detail="Configuration not found for this plugin")

        PluginConfigurationManager.delete_configuration(
            db=db,
            config_id=config_id,
            deleted_by=current_user,
        )
        return None
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("delete_config_error", error=str(e), config_id=str(config_id))
        raise HTTPException(status_code=500, detail="Failed to delete configuration")


@router.get("/{config_id}/history", response_model=ConfigurationHistoryListResponse)
def get_configuration_history(
    plugin_id: UUID,
    config_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get audit trail for a configuration"""
    try:
        config = PluginConfigurationManager.get_configuration(db=db, config_id=config_id)
        if config.plugin_id != plugin_id:
            raise HTTPException(status_code=404, detail="Configuration not found for this plugin")

        history, total = PluginConfigurationManager.get_configuration_history(
            db=db,
            config_id=config_id,
            skip=skip,
            limit=limit,
        )
        return ConfigurationHistoryListResponse(
            history=history,
            total=total,
            skip=skip,
            limit=limit,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("get_config_history_error", error=str(e), config_id=str(config_id))
        raise HTTPException(status_code=500, detail="Failed to get configuration history")
