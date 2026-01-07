// Krystal Code Simplifier
// Organizes and simplifies Krystal code while preserving functionality
// Respects protected sections marked with @noformat directives

/// Configuration for the code simplifier
#[derive(Debug, Clone)]
pub struct SimplifierConfig {
    /// Enable/disable simplification
    pub enabled: bool,
    /// Normalize whitespace
    pub normalize_whitespace: bool,
    /// Remove redundant operations
    pub remove_redundant: bool,
    /// Simplify arithmetic expressions
    pub simplify_expressions: bool,
    /// Sort imports/modules
    pub sort_modules: bool,
}

impl Default for SimplifierConfig {
    fn default() -> Self {
        SimplifierConfig {
            enabled: true,
            normalize_whitespace: true,
            remove_redundant: false, // TODO: Implement proper block-aware redundancy removal
            simplify_expressions: false,
            sort_modules: false,
        }
    }
}

/// Protected region marker
#[derive(Debug, Clone)]
struct ProtectedRegion {
    start: usize,
    end: usize,
}

pub struct KrystalSimplifier {
    config: SimplifierConfig,
}

impl KrystalSimplifier {
    pub fn new(config: SimplifierConfig) -> Self {
        KrystalSimplifier { config }
    }

    pub fn with_default() -> Self {
        KrystalSimplifier {
            config: SimplifierConfig::default(),
        }
    }

    /// Simplify Krystal source code
    /// Respects @noformat and @noformat_end markers
    pub fn simplify(&self, source: &str) -> Result<String, String> {
        if !self.config.enabled {
            return Ok(source.to_string());
        }

        // Find protected regions
        let protected_regions = self.find_protected_regions(source);

        // Split source into protected and unprotected parts
        let segments = self.split_by_protected_regions(source, &protected_regions);

        // Process each segment
        let mut result = String::new();
        for (content, is_protected) in segments {
            if is_protected {
                // Don't modify protected regions
                result.push_str(&content);
            } else {
                // Simplify unprotected regions
                let simplified = self.simplify_segment(&content)?;
                result.push_str(&simplified);
            }
        }

        Ok(result)
    }

    /// Find regions marked with @noformat ... @noformat_end
    fn find_protected_regions(&self, source: &str) -> Vec<ProtectedRegion> {
        let mut regions = Vec::new();
        let mut current_start: Option<usize> = None;

        for (idx, line) in source.lines().enumerate() {
            let trimmed = line.trim();
            
            if trimmed == "# @noformat" || trimmed == "#@noformat" {
                if current_start.is_none() {
                    current_start = Some(self.line_to_byte_offset(source, idx));
                }
            } else if trimmed == "# @noformat_end" || trimmed == "#@noformat_end" {
                if let Some(start) = current_start {
                    let end = self.line_to_byte_offset(source, idx + 1);
                    regions.push(ProtectedRegion { start, end });
                    current_start = None;
                }
            }
        }

        regions
    }

    /// Convert line number to byte offset
    fn line_to_byte_offset(&self, source: &str, line_num: usize) -> usize {
        source
            .lines()
            .take(line_num)
            .map(|line| line.len() + 1) // +1 for newline
            .sum()
    }

    /// Split source into protected and unprotected segments
    fn split_by_protected_regions(
        &self,
        source: &str,
        protected_regions: &[ProtectedRegion],
    ) -> Vec<(String, bool)> {
        let mut segments = Vec::new();
        let mut last_pos = 0;

        for region in protected_regions {
            // Add unprotected segment before this region
            if region.start > last_pos {
                let content = source[last_pos..region.start].to_string();
                segments.push((content, false));
            }

            // Add protected segment
            let content = source[region.start..region.end].to_string();
            segments.push((content, true));

            last_pos = region.end;
        }

        // Add remaining unprotected content
        if last_pos < source.len() {
            let content = source[last_pos..].to_string();
            segments.push((content, false));
        }

        segments
    }

    /// Simplify an unprotected code segment
    fn simplify_segment(&self, segment: &str) -> Result<String, String> {
        let mut result = segment.to_string();

        if self.config.normalize_whitespace {
            result = self.normalize_whitespace(&result);
        }

        if self.config.remove_redundant {
            result = self.remove_redundant_operations(&result)?;
        }

        if self.config.simplify_expressions {
            result = self.simplify_expressions(&result)?;
        }

        Ok(result)
    }

    /// Normalize whitespace in code
    fn normalize_whitespace(&self, code: &str) -> String {
        let mut result = String::new();
        let mut prev_blank = false;

        for line in code.lines() {
            let trimmed = line.trim();
            
            if trimmed.is_empty() {
                if !prev_blank {
                    result.push('\n');
                    prev_blank = true;
                }
            } else {
                result.push_str(trimmed);
                result.push('\n');
                prev_blank = false;
            }
        }

        result
    }

    /// Remove redundant operations (e.g., translate(0,0,0), scale(1,1,1))
    /// NOTE: Basic implementation - full block-aware removal to be implemented
    fn remove_redundant_operations(&self, code: &str) -> Result<String, String> {
        // TODO: Implement proper block-aware redundancy removal
        // For now, this is a placeholder that returns code unchanged
        // Future implementation should track block structure and remove
        // redundant transformation blocks while preserving their contents
        Ok(code.to_string())
    }

    /// Check if an operation is redundant
    fn is_redundant_operation(&self, line: &str) -> bool {
        // Identity transformations that do nothing
        let redundant_patterns = vec![
            "translate(0, 0, 0)",
            "translate(0,0,0)",
            "scale(1, 1, 1)",
            "scale(1,1,1)",
            "rotate(0,",
        ];

        for pattern in redundant_patterns {
            if line.contains(pattern) {
                return true;
            }
        }

        false
    }

    /// Simplify arithmetic expressions
    fn simplify_expressions(&self, code: &str) -> Result<String, String> {
        // TODO: Implement expression simplification
        // For now, just return the code as-is
        // Future: Parse and simplify expressions like "5 + 5" -> "10"
        Ok(code.to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simplify_with_protected_region() {
        let source = r#"
cube(0, 0, 0, 10)

# @noformat
translate(0, 0, 0) {
    cube(1, 1, 1, 5)
}
# @noformat_end

sphere(10, 10, 10, 5)
"#;

        let simplifier = KrystalSimplifier::with_default();
        let result = simplifier.simplify(source).unwrap();

        // The protected translate(0,0,0) should remain
        assert!(result.contains("translate(0, 0, 0)"));
    }

    #[test]
    #[ignore] // TODO: Implement block-aware redundancy removal
    fn test_remove_redundant_operations() {
        let source = r#"
cube(0, 0, 0, 10)
translate(0, 0, 0) {
    sphere(5, 5, 5, 3)
}
"#;

        let mut config = SimplifierConfig::default();
        config.remove_redundant = true;
        let simplifier = KrystalSimplifier::new(config);
        let result = simplifier.simplify(source).unwrap();

        // The redundant translate should be removed
        assert!(!result.contains("translate(0, 0, 0)"));
        // But the shapes should remain
        assert!(result.contains("cube(0, 0, 0, 10)"));
        assert!(result.contains("sphere(5, 5, 5, 3)"));
    }

    #[test]
    fn test_normalize_whitespace() {
        let source = "cube(0, 0, 0, 10)\n\n\n\nsphere(5, 5, 5, 3)";
        let simplifier = KrystalSimplifier::with_default();
        let result = simplifier.simplify(source).unwrap();

        // Should reduce multiple blank lines to one
        assert!(!result.contains("\n\n\n"));
    }
}
