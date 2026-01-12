package aigeneration

import (
	"embed"
	"fmt"
	"io/fs"
	"path/filepath"
	"strings"

	"github.com/kweaver-ai/operator-hub/operator-integration/server/interfaces"
)

// prompt加载及解析

//go:embed templates/*.md
var promptTemplatesFS embed.FS

// PromptLoader 提示词加载器
type PromptLoader struct {
	templates map[interfaces.PromptTemplateType]*interfaces.PromptTemplate
}

// NewPromptLoader 创建新的提示词加载器
func NewPromptLoader() (*PromptLoader, error) {
	// 创建新的提示词加载器
	loader := &PromptLoader{
		templates: map[interfaces.PromptTemplateType]*interfaces.PromptTemplate{
			interfaces.PythonFunctionGenerator: {
				Name:               string(interfaces.PythonFunctionGenerator),
				Description:        "Python函数生成Prompt模板",
				SystemPrompt:       "",
				UserPromptTemplate: "函数内容描述:%s; inputs:%v; outputs:%v;",
			},
			interfaces.MetadataParamGenerator: {
				Name:               string(interfaces.MetadataParamGenerator),
				Description:        "元数据参数生成Prompt模板",
				SystemPrompt:       "",
				UserPromptTemplate: `{"code": "%s", "inputs_json": %v, "outputs_json": %v}`,
			},
		},
	}

	if err := loader.loadTemplates(); err != nil {
		return nil, fmt.Errorf("failed to load prompt templates: %w", err)
	}

	return loader, nil
}

// loadTemplates 加载所有模板文件
func (l *PromptLoader) loadTemplates() error {
	return fs.WalkDir(promptTemplatesFS, "templates", func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}

		if d.IsDir() || filepath.Ext(path) != ".md" {
			return nil
		}
		tempName := strings.ToLower(strings.TrimSuffix(filepath.Base(path), filepath.Ext(filepath.Base(path))))
		tempType := interfaces.PromptTemplateType(tempName)
		if _, ok := l.templates[tempType]; !ok {
			return fmt.Errorf("prompt template %s not found", tempType)
		}

		content, err := fs.ReadFile(promptTemplatesFS, path)
		if err != nil {
			return fmt.Errorf("failed to read template file %s: %w", path, err)
		}
		l.templates[tempType].SystemPrompt = string(content)
		return nil
	})
}

// GetTemplate 获取指定类型的提示词模板
func (l *PromptLoader) GetTemplate(tempType interfaces.PromptTemplateType) (*interfaces.PromptTemplate, error) {
	if temp, ok := l.templates[tempType]; ok {
		return temp, nil
	}
	return nil, fmt.Errorf("prompt template %s not found", tempType)
}
