# Quick Start

This project is a tool for ***traditional performing arts*** in MEDIAN Lab, which allows you to quickly generate slides based on a given paper title.

Note that the generated contents should be carefully double-checked, some unavoidable mistakes still exist (e.g. wrong personal page).

## Prerequisites

Before using this project, please ensure the following:

1. **Python Installation**:  
   Make sure Python is installed on your system. You can download it from [python.org](https://www.python.org/).

2. **Install Dependencies**:  
   Install the required dependencies by running the following command in your terminal:  
   ```bash
   pip install -r requirements.txt
   ```

3. **API Key Setup**:  
   - Register an account at [serper.dev](https://serper.dev/).  
   - Obtain your API key from your account.  
   - Set your `api_key` in the script by replacing the placeholder in the following line:  
     [get_author_home_page.py - Line 60](https://github.com/shuhao02/PaperCounterMEDIAN/blob/9f81d9e3aac27a09b60bae6269816dd14b66db06/get_author_home_page.py#L60).  
     Example:  
     ```python
     api_key = "your_api_key_here"
     ```


## Steps to Generate Slides

1. Open the `create_slide.py` file and update the `paper_title` variable with the title of your paper.

2. Run the following command in your terminal:
    ```bash
    python create_slide.py
    ```

That's it! The script will generate slides based on the input.

## Contributing

We welcome contributions! Feel free to submit issues or pull requests to improve the project.

## Acknowledgments

This project was developed by:
- [Weisen Jiang](https://github.com/ws-jiang)
- [Shuhao Chen](https://github.com/shuhao02)
- [Zhuang Zhan](https://github.com/zwebrain)

