import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Divider,
  Button,
  Grid,
  ColorPicker,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  TextField
} from '@mui/material';
import {
  ExpandMore,
  Palette,
  TextFields,
  ViewColumn,
  Print,
  Refresh
} from '@mui/icons-material';

interface TemplateCustomizerProps {
  template: any;
  onStyleChange: (styles: TemplateStyles) => void;
  currentStyles?: TemplateStyles;
}

interface TemplateStyles {
  // Typography
  fontFamily: string;
  fontSize: number;
  lineHeight: number;
  
  // Colors
  primaryColor: string;
  secondaryColor: string;
  textColor: string;
  backgroundColor: string;
  
  // Layout
  maxWidth: number;
  padding: number;
  margin: number;
  
  // Spacing
  headingSpacing: number;
  paragraphSpacing: number;
  
  // Borders and shadows
  borderRadius: number;
  shadowIntensity: number;
  
  // Document specific
  showHeader: boolean;
  showFooter: boolean;
  printOptimized: boolean;
}

const defaultStyles: TemplateStyles = {
  fontFamily: 'Hiragino Sans',
  fontSize: 14,
  lineHeight: 1.8,
  primaryColor: '#22c55e',
  secondaryColor: '#64748b',
  textColor: '#1e293b',
  backgroundColor: '#ffffff',
  maxWidth: 800,
  padding: 32,
  margin: 0,
  headingSpacing: 32,
  paragraphSpacing: 16,
  borderRadius: 8,
  shadowIntensity: 0.1,
  showHeader: true,
  showFooter: true,
  printOptimized: false
};

const fontOptions = [
  { value: 'Hiragino Sans', label: 'Hiragino Sans（ヒラギノ角ゴ）' },
  { value: 'Yu Gothic', label: 'Yu Gothic（游ゴシック）' },
  { value: 'Meiryo', label: 'Meiryo（メイリオ）' },
  { value: 'MS Gothic', label: 'MS Gothic（MS ゴシック）' },
  { value: 'Yu Mincho', label: 'Yu Mincho（游明朝）' },
  { value: 'MS Mincho', label: 'MS Mincho（MS 明朝）' },
  { value: 'Hiragino Mincho ProN', label: 'Hiragino Mincho ProN（ヒラギノ明朝）' }
];

const ColorBox: React.FC<{ color: string; onChange: (color: string) => void; label: string }> = ({
  color,
  onChange,
  label
}) => (
  <Box>
    <Typography variant="body2" mb={1}>{label}</Typography>
    <Box
      sx={{
        width: 40,
        height: 40,
        backgroundColor: color,
        border: 1,
        borderColor: 'divider',
        borderRadius: 1,
        cursor: 'pointer',
        '&:hover': {
          boxShadow: 2
        }
      }}
      onClick={() => {
        // In a real implementation, this would open a color picker
        const newColor = prompt('色を入力してください (例: #22c55e)', color);
        if (newColor) onChange(newColor);
      }}
    />
  </Box>
);

export const TemplateCustomizer: React.FC<TemplateCustomizerProps> = ({
  template,
  onStyleChange,
  currentStyles = defaultStyles
}) => {
  const [styles, setStyles] = useState<TemplateStyles>(currentStyles);

  const handleStyleChange = (key: keyof TemplateStyles, value: any) => {
    const newStyles = { ...styles, [key]: value };
    setStyles(newStyles);
    onStyleChange(newStyles);
  };

  const resetToDefaults = () => {
    setStyles(defaultStyles);
    onStyleChange(defaultStyles);
  };

  const generatePreviewCSS = () => {
    return `
      <style>
        body {
          font-family: "${styles.fontFamily}", sans-serif;
          font-size: ${styles.fontSize}px;
          line-height: ${styles.lineHeight};
          color: ${styles.textColor};
          background-color: ${styles.backgroundColor};
          max-width: ${styles.maxWidth}px;
          padding: ${styles.padding}px;
          margin: ${styles.margin}px auto;
        }
        h1, h2, h3 {
          color: ${styles.textColor};
          margin-bottom: ${styles.headingSpacing}px;
        }
        h1 {
          border-bottom: 2px solid ${styles.primaryColor};
        }
        h2 {
          border-left: 4px solid ${styles.primaryColor};
          padding-left: 16px;
          background: linear-gradient(90deg, ${styles.backgroundColor}, transparent);
        }
        p {
          margin: ${styles.paragraphSpacing}px 0;
        }
        .card {
          background: ${styles.backgroundColor};
          border-radius: ${styles.borderRadius}px;
          box-shadow: 0 2px 8px rgba(0,0,0,${styles.shadowIntensity});
          padding: 16px;
          margin: 16px 0;
        }
        .primary-color {
          color: ${styles.primaryColor};
        }
        .secondary-color {
          color: ${styles.secondaryColor};
        }
        @media print {
          body {
            ${styles.printOptimized ? 'font-size: 12px; padding: 20px;' : ''}
          }
        }
      </style>
    `;
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">
          テンプレートカスタマイズ
        </Typography>
        <Button
          startIcon={<Refresh />}
          onClick={resetToDefaults}
          variant="outlined"
          size="small"
        >
          リセット
        </Button>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          {/* Typography Settings */}
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box display="flex" alignItems="center" gap={1}>
                <TextFields />
                <Typography>フォント・タイポグラフィ</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Box space={2}>
                <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                  <InputLabel>フォント</InputLabel>
                  <Select
                    value={styles.fontFamily}
                    label="フォント"
                    onChange={(e) => handleStyleChange('fontFamily', e.target.value)}
                  >
                    {fontOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <Typography variant="body2" mb={1}>
                  フォントサイズ: {styles.fontSize}px
                </Typography>
                <Slider
                  value={styles.fontSize}
                  onChange={(_, value) => handleStyleChange('fontSize', value)}
                  min={10}
                  max={24}
                  step={1}
                  sx={{ mb: 2 }}
                />

                <Typography variant="body2" mb={1}>
                  行間: {styles.lineHeight}
                </Typography>
                <Slider
                  value={styles.lineHeight}
                  onChange={(_, value) => handleStyleChange('lineHeight', value)}
                  min={1.0}
                  max={2.5}
                  step={0.1}
                  sx={{ mb: 2 }}
                />
              </Box>
            </AccordionDetails>
          </Accordion>

          {/* Color Settings */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box display="flex" alignItems="center" gap={1}>
                <Palette />
                <Typography>カラー設定</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <ColorBox
                    color={styles.primaryColor}
                    onChange={(color) => handleStyleChange('primaryColor', color)}
                    label="プライマリカラー"
                  />
                </Grid>
                <Grid item xs={6}>
                  <ColorBox
                    color={styles.secondaryColor}
                    onChange={(color) => handleStyleChange('secondaryColor', color)}
                    label="セカンダリカラー"
                  />
                </Grid>
                <Grid item xs={6}>
                  <ColorBox
                    color={styles.textColor}
                    onChange={(color) => handleStyleChange('textColor', color)}
                    label="テキストカラー"
                  />
                </Grid>
                <Grid item xs={6}>
                  <ColorBox
                    color={styles.backgroundColor}
                    onChange={(color) => handleStyleChange('backgroundColor', color)}
                    label="背景色"
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>

          {/* Layout Settings */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box display="flex" alignItems="center" gap={1}>
                <ViewColumn />
                <Typography>レイアウト</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Box>
                <Typography variant="body2" mb={1}>
                  最大幅: {styles.maxWidth}px
                </Typography>
                <Slider
                  value={styles.maxWidth}
                  onChange={(_, value) => handleStyleChange('maxWidth', value)}
                  min={600}
                  max={1200}
                  step={50}
                  sx={{ mb: 2 }}
                />

                <Typography variant="body2" mb={1}>
                  パディング: {styles.padding}px
                </Typography>
                <Slider
                  value={styles.padding}
                  onChange={(_, value) => handleStyleChange('padding', value)}
                  min={16}
                  max={80}
                  step={8}
                  sx={{ mb: 2 }}
                />

                <Typography variant="body2" mb={1}>
                  見出し間隔: {styles.headingSpacing}px
                </Typography>
                <Slider
                  value={styles.headingSpacing}
                  onChange={(_, value) => handleStyleChange('headingSpacing', value)}
                  min={16}
                  max={64}
                  step={8}
                  sx={{ mb: 2 }}
                />

                <Typography variant="body2" mb={1}>
                  段落間隔: {styles.paragraphSpacing}px
                </Typography>
                <Slider
                  value={styles.paragraphSpacing}
                  onChange={(_, value) => handleStyleChange('paragraphSpacing', value)}
                  min={8}
                  max={32}
                  step={4}
                  sx={{ mb: 2 }}
                />
              </Box>
            </AccordionDetails>
          </Accordion>

          {/* Print Settings */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box display="flex" alignItems="center" gap={1}>
                <Print />
                <Typography>印刷・その他</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Box>
                <FormControlLabel
                  control={
                    <Switch
                      checked={styles.showHeader}
                      onChange={(e) => handleStyleChange('showHeader', e.target.checked)}
                    />
                  }
                  label="ヘッダーを表示"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={styles.showFooter}
                      onChange={(e) => handleStyleChange('showFooter', e.target.checked)}
                    />
                  }
                  label="フッターを表示"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={styles.printOptimized}
                      onChange={(e) => handleStyleChange('printOptimized', e.target.checked)}
                    />
                  }
                  label="印刷最適化"
                />

                <Typography variant="body2" mb={1} mt={2}>
                  角丸: {styles.borderRadius}px
                </Typography>
                <Slider
                  value={styles.borderRadius}
                  onChange={(_, value) => handleStyleChange('borderRadius', value)}
                  min={0}
                  max={16}
                  step={2}
                  sx={{ mb: 2 }}
                />

                <Typography variant="body2" mb={1}>
                  影の強さ: {styles.shadowIntensity}
                </Typography>
                <Slider
                  value={styles.shadowIntensity}
                  onChange={(_, value) => handleStyleChange('shadowIntensity', value)}
                  min={0}
                  max={0.3}
                  step={0.05}
                  sx={{ mb: 2 }}
                />
              </Box>
            </AccordionDetails>
          </Accordion>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, maxHeight: 600, overflow: 'auto' }}>
            <Typography variant="subtitle1" mb={2}>
              プレビュー
            </Typography>
            <Box
              sx={{
                border: 1,
                borderColor: 'divider',
                borderRadius: 1,
                overflow: 'auto',
                backgroundColor: styles.backgroundColor
              }}
            >
              <Box
                dangerouslySetInnerHTML={{
                  __html: `
                    ${generatePreviewCSS()}
                    <div>
                      <h1>サンプル文書タイトル</h1>
                      <div class="card">
                        <h2>セクション見出し</h2>
                        <p>これはサンプルの段落です。日本語の文書において、適切な行間や文字サイズが重要です。</p>
                        <p class="primary-color">プライマリカラーのテキスト</p>
                        <p class="secondary-color">セカンダリカラーのテキスト</p>
                      </div>
                      <h3>小見出し</h3>
                      <p>より小さな見出しのスタイルです。</p>
                    </div>
                  `
                }}
                sx={{ p: 2 }}
              />
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default TemplateCustomizer;