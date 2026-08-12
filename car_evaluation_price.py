#import libraries
import pandas as pd
import numpy as np
import joblib 
import streamlit as st

#set page config
st.set_page_config(
    page_title="Car price evaluation",
    page_icon= "🚗",
    layout="centered"
)

@st.cache_resource
def load_model_artifact():
    try:
        model = joblib.load("rm_model_car_price_prediction.pkl")
        scaler = joblib.load("scaler_features.pkl")
        label_encoder = joblib.load("label_encoder.pkl")
        feature_columns = joblib.load("feature_columns.pkl")

        return model, scaler, label_encoder, feature_columns
    except FileNotFoundError as e:
        st.error(f"Model file not found: {e}")
        st.stop()
    except Exception as e:
        st.error(f"An error occured: {e}")
        st.stop()

@st.cache_data
def load_dataset():
    try:
        df = pd.read_csv("data/automation-analysis-cleaned-dataset.csv")
        return df
    except FileNotFoundError as e:
        st.error(f"Dataset not found: {e}")
        st.stop

#get filtered option
def get_filtered_option(df, model=None, make=None, condition=None):
    filtered_df = df.copy()

    if model:
        filtered_df = filtered_df[filtered_df['Model'] == model]

    if make:
        filtered_df = filtered_df[filtered_df['Make'] == make]

    if condition:
        filtered_df = filtered_df[filtered_df['Condition'] == condition]

    option = {
        "Years": sorted(filtered_df['Year'].unique().tolist(), reverse=True),
        "Makes": sorted(filtered_df['Make'].unique().tolist()),
        "Models": sorted(filtered_df['Model'].unique().tolist()) if make else sorted(df['Model'].unique().tolist()),
        "Condition": sorted(filtered_df['Condition'].unique().tolist()) if make or model else sorted(df['Condition'].unique().tolist()),
        "Transmission": sorted(filtered_df['Transmission'].unique().tolist()) if make or model or condition else sorted(df['Transmission'].unique().tolist())
    }

    return option

def predict_price(car_data, model, scaler, label_encoder, feature_columns):
    try:
        input_df = pd.DataFrame([car_data])

        columns = ['Make', 'Model', 'Transmission', 'Condition']

        for col in columns:
            if col in label_encoder:
                try:
                    input_df[col + "_encoded"] = label_encoder[col].transform(input_df[col])
                except Exception as e:
                    st.warning(f"Unknown {col}: {car_data[col]}")
                    st.stop()
        #feature preparing
        feature_dict = {
            "Year": car_data["Year"],
            "Make_encoded": input_df["Make_encoded"].values[0],
            "Model_encoded": input_df["Model_encoded"].values[0],
            "Condition_encoded": input_df['Condition_encoded'].values[0],
            "Transmission_encoded": input_df["Transmission_encoded"].values[0]
        }

        #create feaure array
        features = np.array([[feature_dict[col] for col in feature_columns]])

        #scaler feature
        feature_scale =  scaler.transform(features)

        #model prediction
        predicted_price = model.predict(feature_scale)[0]

        margin_percentage = 0.15
        min_predicted_price = predicted_price * (1 - margin_percentage)
        max_predicted_price = predicted_price * (1 + margin_percentage)

        return {
            "predicted_price": predicted_price,
            "min_predicted_price": min_predicted_price,
            "max_predicted_price": max_predicted_price
        }
    except Exception as e:
        st.error(f"An error occured: {e}")
        st.stop

def main():

    st.title("🚗 JiJi Car Evaluation System")
    st.write("Fill all the fields and get immediate car price results.")
    #load model artifact
    model, scaler, label_encoder, feature_columns = load_model_artifact()
    # load dataset
    df = load_dataset()

    #initialize session state
    if "selected_make" not in st.session_state:
        st.session_state.selected_make = None

    if "selected_condition" not in st.session_state:
        st.session_state.selected_condition = None

    if "show_result" not in st.session_state:
        st.session_state.show_result = False
    #get_filtered_option
    option= get_filtered_option(df)

    make = st.selectbox(
        "Make*",
        options=[""] + option["Makes"],
        format_func=lambda x: "Selected Make" if x == "" else x
    )

    if make and make != st.session_state.selected_make:
        st.session_state.selected_make = make
        st.session_state.selected_model = None
        st.session_state.selected_condition = None
        st.session_state.show_result = False

    if make:
        option= get_filtered_option(df, make=make)

    model_name = st.selectbox(
        "Model*",
        options=[''] + option['Models'],
        format_func=lambda x: "Selected Model" if x == "" else x,
        disabled=not make
    )

    if model_name and model_name != st.session_state.selected_model:
            st.session_state.selected_model = model_name
            st.session_state.selected_condition = None
            st.session_state.show_result = False

    if make and model_name:
        option= get_filtered_option(df, make=make, model=model_name)

    year = st.selectbox(
        "Year*", 
        options=[''] + option['Years'],
        format_func=lambda x: "Selected Year" if x == "" else str(x),
        disabled= not (make and model_name)
    )

    if year:
        st.session_state.show_result = False

    condition = st.selectbox(
        "Condition*",
        options=[''] + option['Condition'],
        format_func=lambda x: "Selected Condition" if x == "" else x,
        disabled= not (make and model_name and year)
    )

    if condition and condition != st.session_state.selected_condition:
        st.session_state.selected_condition = condition
        st.session_state.show_result = False

    if make and model_name and condition:
        option = get_filtered_option(df, make=make, model=model_name, condition=condition)

    transmission = st.selectbox(
        "Transmission*",
        options=[""] + option["Transmission"],
        format_func=lambda x: "Selected Transmission" if x == "" else x,
        disabled= not (make and model_name and year and condition)
    )

    if transmission:
        st.session_state.show_result = False

    #get result
    if st.button("Get Result"):
        if not all([make, model_name, year, condition, transmission]):
            st.warning("Please fill all fields")
        else:
            car_data = {
                "Make":make,
                "Model": model_name,
                "Year": year,
                "Condition": condition,
                "Transmission": transmission
            }

            with st.spinner("Calculating the predicted price ..."):
                result = predict_price(car_data,model, scaler, label_encoder, feature_columns)

            if result:
                st.session_state.show_result = True
                st.session_state.result = result
                st.session_state.car_data = car_data

    #display result
    if st.session_state.show_result and 'result' in st.session_state:
        result = st.session_state.result
        car_data = st.session_state.car_data

        #display car detail
        st.markdown("---")
        st.subheader(f"Estimated car price: {car_data['Year']} {car_data['Make']} {car_data['Model']}")

        #predicted price
        st.success(f"## ₦ {result['predicted_price']:,.0f}")

        #price range
        st.write(f"** Price range: {result['min_predicted_price']:,.0f} - {result['max_predicted_price']:,.0f}")

        #car detail
        st.write(f"** Condition {car_data['Condition']} | ** Transmission {car_data['Transmission']}")


if __name__ == "__main__":
    main()