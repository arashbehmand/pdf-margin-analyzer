# PDF Margin Analyzer

PDF Margin Analyzer is a command-line tool designed to help users analyze and adjust the margins of PDF documents. This tool is particularly useful for those who want to optimize their PDFs for better readability or presentation. By calculating and adjusting the margins, you can ensure that your PDFs have consistent and appropriate spacing around the content.

## Features

- Detect margins in PDF documents
- Calculate margin statistics
- Plot margin distributions
- Identify pages with bad margins
- Calculate margins to cut for desired margins

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/arashbehmand/pdf-margin-analyzer.git
   cd pdf-margin-analyzer
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

```
python pdf_margin_analyzer.py [-h] [--exceptions EXCEPTIONS [EXCEPTIONS ...]]
                              [--inner-outer] [--plot]
                              [--adjust-to-desired-margins LEFT/INNER RIGHT/OUTER TOP BOTTOM]
                              pdf_path
```

### Arguments

- `pdf_path`: Path to the PDF file
- `--exceptions`: List of pages to exclude (0-based index)
- `--inner-outer`: Use inner/outer instead of left/right
- `--plot`: Plot margin statistics
- `--adjust`:  Adjust margins to desired values as percentages. Use (left, right, top, bottom)
               or (inner, outer, top, bottom) if `--inner-outer` is specified

### Examples

1. Analyze margins in a PDF file:
   ```
   python pdf_margin_analyzer.py path/to/your/file.pdf
   ```

2. Analyze margins, excluding the first two pages:
   ```
   python pdf_margin_analyzer.py path/to/your/file.pdf --exceptions 0 1
   ```

3. Analyze margins and plot statistics:
   ```
   python pdf_margin_analyzer.py path/to/your/file.pdf --plot
   ```

4. Analyze margins and adjust to desired margins (percentages):
   ```
   python pdf_margin_analyzer.py path/to/your/file.pdf --adjust-to-desired-margins 2 2 2 2
   ```

5. Analyze margins in inner/outer mode and adjust to desired margins (percentages):
   ```
   python pdf_margin_analyzer.py path/to/your/file.pdf --inner-outer --adjust-to-desired-margins 2 2 2 2
   ```

## Integration with pdfarranger

I often use PDF Margin Analyzer in conjunction with [pdfarranger](https://github.com/pdfarranger/pdfarranger) to achieve optimal margins for my PDFs. pdfarranger is a great tool for visually arranging, rearranging, and merging PDF documents. By first analyzing and adjusting the margins with PDF Margin Analyzer, I can ensure that the final output from pdfarranger has consistent and well-optimized margins.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.