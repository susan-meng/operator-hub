package metadata

import (
	"github.com/kweaver-ai/operator-hub/operator-integration/server/interfaces"
	"github.com/kweaver-ai/operator-hub/operator-integration/server/interfaces/model"
	"github.com/kweaver-ai/operator-hub/operator-integration/server/utils"
)

// MetadataDBToStruct 将数据库模型转换为元数据接口
func MetadataDBToStruct(metadataDB interfaces.IMetadataDB) *interfaces.MetadataInfo {
	switch v := metadataDB.(type) {
	case *model.FunctionMetadataDB:
		apiMetadataDB := &model.APIMetadataDB{
			Version:     v.Version,
			Summary:     v.Summary,
			Description: v.Description,
			ServerURL:   v.ServerURL,
			Path:        v.Path,
			Method:      v.Method,
			CreateTime:  v.CreateTime,
			UpdateTime:  v.UpdateTime,
			CreateUser:  v.CreateUser,
			UpdateUser:  v.UpdateUser,
			APISpec:     v.APISpec,
		}
		metadata := apimetadataDBToAPIMetadata(apiMetadataDB)
		dependencies := []string{}
		if v.Dependencies != "" {
			_ = utils.StringToObject(v.Dependencies, &dependencies)
		}
		metadata.FunctionContent = &interfaces.FunctionContent{
			ScriptType:   interfaces.ScriptType(v.GetScriptType()),
			Code:         v.Code,
			Dependencies: dependencies,
		}
		return metadata
	case *model.APIMetadataDB:
		return apimetadataDBToAPIMetadata(v)
	default:
		return nil
	}
}

// apimetadataDBToAPIMetadata 将数据库模型转换为 API 元数据接口
func apimetadataDBToAPIMetadata(metadataDB *model.APIMetadataDB) *interfaces.MetadataInfo {
	apiSpec := &interfaces.APISpec{}
	_ = utils.StringToObject(metadataDB.APISpec, apiSpec)
	return &interfaces.MetadataInfo{
		Version:     metadataDB.Version,
		Summary:     metadataDB.Summary,
		Description: metadataDB.Description,
		ServerURL:   metadataDB.ServerURL,
		Path:        metadataDB.Path,
		Method:      metadataDB.Method,
		CreateTime:  metadataDB.CreateTime,
		UpdateTime:  metadataDB.UpdateTime,
		CreateUser:  metadataDB.CreateUser,
		UpdateUser:  metadataDB.UpdateUser,
		APISpec:     apiSpec,
	}
}
