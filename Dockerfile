FROM python:3.12.0
RUN mkdir -p /dsa3101-2310-14-CARPARK
WORKDIR /dsa3101-2310-14-CARPARK
COPY . /dsa3101-2310-14-CARPARK/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install --upgrade dash flask

# RUN nmp update
# RUN npm install
RUN rm -rf /cashe_dir
ENTRYPOINT ["python", "./frontend/app.py", host='127.0.0.1', port=8050]

# RUN $(npm bin)/ng build --prod
# FROM nginx
# COPY --from=builder /dsa3101-2310-14-CARPARK/* /usr/share/nginx/html
# EXPOSE 80