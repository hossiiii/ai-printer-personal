import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Divider
} from '@mui/material';
import {
  Preview,
  Close,
  Palette,
  Description,
  Style,
  Assignment,
  Event,
  Business
} from '@mui/icons-material';
import { DocumentType } from '../types';

interface Template {
  id: string;
  name: string;
  description: string;
  documentType: DocumentType;
  style: 'japanese_professional' | 'japanese_modern' | 'japanese_formal';
  preview: string;
  variables: string[];
}

interface TemplateSelectorProps {
  documentType: DocumentType;
  onTemplateSelect: (template: Template) => void;
  selectedTemplate?: Template;
}

const getDocumentTypeIcon = (type: DocumentType) => {
  switch (type) {
    case DocumentType.MEETING_MINUTES:
      return <Assignment />;
    case DocumentType.LETTER:
      return <Description />;
    case DocumentType.REPORT:
      return <Business />;
    case DocumentType.FLYER:
      return <Event />;
    default:
      return <Description />;
  }
};

const getDocumentTypeLabel = (type: DocumentType) => {
  switch (type) {
    case DocumentType.MEETING_MINUTES:
      return '会議議事録';
    case DocumentType.LETTER:
      return '手紙・文書';
    case DocumentType.REPORT:
      return 'レポート';
    case DocumentType.FLYER:
      return 'フライヤー';
    default:
      return '文書';
  }
};

const getStyleLabel = (style: string) => {
  switch (style) {
    case 'japanese_professional':
      return 'プロフェッショナル';
    case 'japanese_modern':
      return 'モダン';
    case 'japanese_formal':
      return 'フォーマル';
    default:
      return 'スタンダード';
  }
};

const mockTemplates: Template[] = [
  {
    id: 'meeting-professional',
    name: '会議議事録（プロフェッショナル）',
    description: 'ビジネス会議に適したプロフェッショナルなデザイン',
    documentType: DocumentType.MEETING_MINUTES,
    style: 'japanese_professional',
    preview: `
      <div style="font-family: 'Hiragino Sans', sans-serif; padding: 20px; background: white;">
        <h1 style="text-align: center; border-bottom: 2px solid #22c55e; padding-bottom: 16px;">
          週次定例会議
        </h1>
        <div style="background: #f8f9fa; padding: 16px; border-radius: 8px; margin: 16px 0;">
          <strong>日時：</strong>2024年7月12日<br>
          <strong>出席者：</strong>田中、佐藤、鈴木
        </div>
        <h2 style="background: linear-gradient(90deg, #f8f9fa, transparent); padding: 8px 16px; border-left: 4px solid #22c55e;">
          議題
        </h2>
        <ol>
          <li>プロジェクト進捗確認</li>
          <li>来月の計画</li>
        </ol>
      </div>
    `,
    variables: ['meeting_title', 'meeting_date', 'attendees', 'agenda_items']
  },
  {
    id: 'meeting-modern',
    name: '会議議事録（モダン）',
    description: 'モダンで視覚的に魅力的なデザイン',
    documentType: DocumentType.MEETING_MINUTES,
    style: 'japanese_modern',
    preview: `
      <div style="font-family: 'Hiragino Sans', sans-serif; padding: 20px; background: linear-gradient(135deg, #fafafa, #ffffff);">
        <div style="background: linear-gradient(135deg, #22c55e, #16a34a); color: white; padding: 8px 16px; border-radius: 20px; display: inline-block; margin-bottom: 20px;">
          2024年7月12日
        </div>
        <h1 style="font-size: 28px; text-align: center; position: relative;">
          週次定例会議
          <div style="position: absolute; bottom: -12px; left: 50%; transform: translateX(-50%); width: 80px; height: 3px; background: linear-gradient(90deg, #22c55e, #ef2b70); border-radius: 2px;"></div>
        </h1>
        <div style="background: white; padding: 24px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
          <h2>📋 会議概要</h2>
          <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <span style="background: #f1f5f9; padding: 6px 12px; border-radius: 16px; font-size: 13px;">田中</span>
            <span style="background: #f1f5f9; padding: 6px 12px; border-radius: 16px; font-size: 13px;">佐藤</span>
          </div>
        </div>
      </div>
    `,
    variables: ['meeting_title', 'meeting_date', 'attendees', 'agenda_items']
  },
  {
    id: 'letter-formal',
    name: '正式な手紙（フォーマル）',
    description: '正式なビジネス文書に適したクラシックなデザイン',
    documentType: DocumentType.LETTER,
    style: 'japanese_formal',
    preview: `
      <div style="font-family: 'Yu Mincho', serif; padding: 40px; background: white; max-width: 600px;">
        <div style="text-align: right; margin-bottom: 40px;">令和6年7月12日</div>
        <div style="text-align: center; border: 1px solid #ccc; padding: 20px; background: #fafafa; margin: 30px 0;">
          株式会社サンプル<br>
          代表取締役 田中様
        </div>
        <h1 style="text-align: center; border: 2px solid #1a1a1a; padding: 20px; position: relative;">
          お礼のご挨拶
        </h1>
        <p style="text-indent: 1em; line-height: 1.9;">
          拝啓　時下ますますご清栄のこととお慶び申し上げます。
        </p>
      </div>
    `,
    variables: ['sender_name', 'recipient_name', 'subject', 'body']
  },
  {
    id: 'report-professional',
    name: 'レポート（プロフェッショナル）',
    description: 'ビジネスレポートに適したプロフェッショナルなデザイン',
    documentType: DocumentType.REPORT,
    style: 'japanese_professional',
    preview: `
      <div style="font-family: 'Hiragino Sans', sans-serif; padding: 20px; background: white;">
        <div style="background: linear-gradient(135deg, #22c55e, #16a34a); color: white; padding: 8px 16px; border-radius: 20px; display: inline-block; margin-bottom: 20px;">
          2024年7月12日
        </div>
        <h1 style="text-align: center; border-bottom: 2px solid #22c55e; padding-bottom: 16px;">
          四半期売上レポート
        </h1>
        <div style="background: #f8f9fa; padding: 16px; border-radius: 8px; margin: 16px 0;">
          <h2>📊 概要</h2>
          <p><strong>作成者：</strong>営業部 田中</p>
          <p>本四半期の売上実績と分析結果をまとめました。</p>
        </div>
      </div>
    `,
    variables: ['report_title', 'author', 'summary', 'content_sections']
  }
];

export const TemplateSelector: React.FC<TemplateSelectorProps> = ({
  documentType,
  onTemplateSelect,
  selectedTemplate
}) => {
  const [filteredTemplates, setFilteredTemplates] = useState<Template[]>([]);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewTemplate, setPreviewTemplate] = useState<Template | null>(null);
  const [styleFilter, setStyleFilter] = useState<string>('all');

  useEffect(() => {
    let filtered = mockTemplates.filter(template => template.documentType === documentType);
    
    if (styleFilter !== 'all') {
      filtered = filtered.filter(template => template.style === styleFilter);
    }
    
    setFilteredTemplates(filtered);
  }, [documentType, styleFilter]);

  const handlePreview = (template: Template) => {
    setPreviewTemplate(template);
    setPreviewOpen(true);
  };

  const handleSelect = (template: Template) => {
    onTemplateSelect(template);
    setPreviewOpen(false);
  };

  return (
    <Box>
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        {getDocumentTypeIcon(documentType)}
        <Typography variant="h6">
          {getDocumentTypeLabel(documentType)}のテンプレート選択
        </Typography>
      </Box>

      <Box mb={3}>
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel>スタイル</InputLabel>
          <Select
            value={styleFilter}
            label="スタイル"
            onChange={(e) => setStyleFilter(e.target.value)}
          >
            <MenuItem value="all">すべて</MenuItem>
            <MenuItem value="japanese_professional">プロフェッショナル</MenuItem>
            <MenuItem value="japanese_modern">モダン</MenuItem>
            <MenuItem value="japanese_formal">フォーマル</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Grid container spacing={3}>
        {filteredTemplates.map((template) => (
          <Grid item xs={12} md={6} key={template.id}>
            <Card 
              sx={{ 
                height: '100%',
                cursor: 'pointer',
                border: selectedTemplate?.id === template.id ? 2 : 1,
                borderColor: selectedTemplate?.id === template.id ? 'primary.main' : 'divider',
                '&:hover': {
                  boxShadow: 4,
                  transform: 'translateY(-2px)'
                },
                transition: 'all 0.2s ease'
              }}
              onClick={() => handleSelect(template)}
            >
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Typography variant="h6" component="h3">
                    {template.name}
                  </Typography>
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      handlePreview(template);
                    }}
                  >
                    <Preview />
                  </IconButton>
                </Box>
                
                <Typography variant="body2" color="text.secondary" mb={2}>
                  {template.description}
                </Typography>
                
                <Box display="flex" gap={1} mb={2}>
                  <Chip
                    icon={<Style />}
                    label={getStyleLabel(template.style)}
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                  <Chip
                    icon={<Palette />}
                    label={`${template.variables.length}個の変数`}
                    size="small"
                    variant="outlined"
                  />
                </Box>

                <Box
                  sx={{
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 1,
                    overflow: 'hidden',
                    height: 120,
                    backgroundColor: '#fafafa'
                  }}
                >
                  <Box
                    dangerouslySetInnerHTML={{ __html: template.preview }}
                    sx={{
                      transform: 'scale(0.3)',
                      transformOrigin: 'top left',
                      width: '333%',
                      height: '333%',
                      overflow: 'hidden'
                    }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {filteredTemplates.length === 0 && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            選択された条件に該当するテンプレートがありません。
          </Typography>
        </Paper>
      )}

      <Dialog
        open={previewOpen}
        onClose={() => setPreviewOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              {previewTemplate?.name}
            </Typography>
            <IconButton onClick={() => setPreviewOpen(false)}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {previewTemplate && (
            <Box>
              <Box mb={2}>
                <Typography variant="body2" color="text.secondary">
                  {previewTemplate.description}
                </Typography>
              </Box>
              
              <Divider sx={{ mb: 2 }} />
              
              <Box
                sx={{
                  border: 1,
                  borderColor: 'divider',
                  borderRadius: 1,
                  overflow: 'auto',
                  maxHeight: 400,
                  backgroundColor: 'white'
                }}
              >
                <Box
                  dangerouslySetInnerHTML={{ __html: previewTemplate.preview }}
                  sx={{ p: 2 }}
                />
              </Box>
              
              <Box mt={2} display="flex" justifyContent="flex-end" gap={2}>
                <Button
                  variant="outlined"
                  onClick={() => setPreviewOpen(false)}
                >
                  キャンセル
                </Button>
                <Button
                  variant="contained"
                  onClick={() => handleSelect(previewTemplate)}
                >
                  このテンプレートを選択
                </Button>
              </Box>
            </Box>
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default TemplateSelector;