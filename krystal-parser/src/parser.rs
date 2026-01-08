// Krystal Parser Implementation
// NOTE: This is a partial implementation - geometry evaluation to be added later

use pest::Parser;
use pest_derive::Parser;
use crate::ast::*;

#[derive(Parser)]
#[grammar = "krystal.pest"]
pub struct KrystalParser;

impl KrystalParser {
    /// Parse Krystal source code into an AST
    /// NOTE: This parser validates syntax but does not evaluate geometry
    /// Full geometry backend implementation is pending
    pub fn parse_program(source: &str) -> Result<Program, String> {
        let pairs = Self::parse(Rule::program, source)
            .map_err(|e| format!("Parse error: {}", e))?;
        
        let mut statements = Vec::new();
        
        for pair in pairs {
            match pair.as_rule() {
                Rule::program => {
                    for inner_pair in pair.into_inner() {
                        if let Rule::statement = inner_pair.as_rule() {
                            // Parse statement - partial implementation
                            // Full statement parsing to be completed
                            statements.push(Self::parse_statement_stub(inner_pair)?);
                        }
                    }
                }
                Rule::EOI => {}
                _ => {}
            }
        }
        
        Ok(Program { statements })
    }
    
    // Stub method - to be fully implemented when geometry backend is ready
    fn parse_statement_stub(_pair: pest::iterators::Pair<Rule>) -> Result<Statement, String> {
        // Placeholder: Returns a simple cube statement
        // TODO: Implement full statement parsing for all statement types
        Ok(Statement::Shape(ShapeStatement {
            shape: Shape::Cube {
                x: Value::Number(0.0),
                y: Value::Number(0.0),
                z: Value::Number(0.0),
                size: Value::Number(10.0),
            },
            name: None,
        }))
    }
    
    /// Validate syntax without building full AST (quick validation)
    pub fn validate_syntax(source: &str) -> Result<(), String> {
        Self::parse(Rule::program, source)
            .map(|_| ())
            .map_err(|e| format!("Syntax error: {}", e))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_simple_cube() {
        let source = "cube(0, 0, 0, 10)";
        let result = KrystalParser::validate_syntax(source);
        assert!(result.is_ok());
    }

    #[test]
    fn test_parse_with_comment() {
        let source = "# This is a comment\ncube(0, 0, 0, 10)";
        let result = KrystalParser::validate_syntax(source);
        assert!(result.is_ok());
    }

    #[test]
    fn test_parse_module() {
        let source = r#"
module box(width, height, depth) {
    cube(0, 0, 0, width)
}
        "#;
        let result = KrystalParser::validate_syntax(source);
        assert!(result.is_ok());
    }
}
