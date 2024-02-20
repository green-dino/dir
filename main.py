import os
import pandas as pd
import re
import streamlit as st

class FileHandler:
    @staticmethod
    def list_files(directory):
        return [f for f in os.listdir(directory) if f.endswith(('.csv', '.xls', '.xlsx'))]

    @staticmethod
    def create_output_directory(directory):
        output_dir = os.path.join(directory, "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        return output_dir

class DataProcessor:
    def __init__(self):
        self.email_pattern = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}')
        self.word_pattern = re.compile(r'\b[a-zA-Z]{5,15}\b')
        self.url_pattern = re.compile(r'\b\w+:\/\/[\w@][\w.:@]+\/?[\w.\.?=%&=\-@$,]*\b')

    def process_data(self, df):
        new_columns = {}
        for column in df.columns:
            if df[column].dtype == 'object':
                new_columns[column + '_emails'] = df[column].apply(lambda x: self.email_pattern.findall(str(x)))
                new_columns[column + '_words'] = df[column].apply(lambda x: self.word_pattern.findall(str(x)))
                new_columns[column + '_urls'] = df[column].apply(lambda x: self.url_pattern.findall(str(x)))
        return pd.concat([df, pd.DataFrame(new_columns)], axis=1)

class DataFrameHandler:
    @staticmethod
    def read_file_to_dataframe(file_path, sheet_name=None):
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith(('.xls', '.xlsx')):
            if sheet_name is None:
                xls = pd.ExcelFile(file_path)
                sheet_name = xls.sheet_names
            if isinstance(sheet_name, list):
                return pd.concat([pd.read_excel(file_path, sheet_name=sheet) for sheet in sheet_name])
            else:
                return pd.read_excel(file_path, sheet_name=sheet_name)
        else:
            raise ValueError("Unsupported file format. Please provide a CSV or XLS/XLSX file.")

    @staticmethod
    def save_dataframe(df, filename, format='csv'):
        if format == 'csv':
            df.to_csv(filename, index=False)
        elif format == 'pickle':
            df.to_pickle(filename)
        else:
            raise ValueError("Unsupported format. Please choose 'csv' or 'pickle'.")

def main():
    st.title("CSV and Excel File Processor")

    file_dir = st.text_input("Enter the directory where the file is stored (type 'exit' to quit):")

    if file_dir.lower() == 'exit':
        st.stop()

    if not file_dir:
        st.warning("Directory path cannot be empty. Please provide a valid directory path.")
        st.stop()

    files = FileHandler.list_files(file_dir)

    if not files:
        st.warning("No CSV or XLS/XLSX files found in the specified directory.")
        st.stop()

    st.write("Files found in the directory:")
    for i, file in enumerate(files, start=1):
        st.write(f"{i}. {file}")

    file_choice = st.number_input("Enter the number corresponding to the file you want to use:", value=1, min_value=1, max_value=len(files))

    file_path = os.path.join(file_dir, files[int(file_choice) - 1])

    sheet_name = st.text_input("Enter the sheet name(s) you want to read (comma-separated, or leave blank to read all):")

    sheet_name = None if not sheet_name else [s.strip() for s in sheet_name.split(',')]

    dataframe = DataFrameHandler.read_file_to_dataframe(file_path, sheet_name)

    st.write("DataFrame Preview:")
    st.write(dataframe)

    output_dir = FileHandler.create_output_directory(file_dir)

    output_filename = st.text_input("Enter the filename for the output file (without extension):")

    format_choice = st.selectbox("Choose output format:", options=['csv', 'pickle'])

    if st.button("Save"):
        try:
            if format_choice.lower() == 'csv':
                output_file = os.path.join(output_dir, f"{output_filename}.csv")
                DataFrameHandler.save_dataframe(dataframe, output_file, 'csv')
                st.success(f"DataFrame saved as CSV: {output_file}")
            elif format_choice.lower() == 'pickle':
                output_file = os.path.join(output_dir, f"{output_filename}.pickle")
                DataFrameHandler.save_dataframe(dataframe, output_file, 'pickle')
                st.success(f"DataFrame saved as pickle: {output_file}")
        except ValueError as ve:
            st.error(f"Error: {ve}")

if __name__ == "__main__":
    main()
