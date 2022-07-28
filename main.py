from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from numpy import require
import pandas as pd
import ast
import requests

class Users(Resource):
    def get(self):
        data = pd.read_csv('users.csv')
        data = data.to_dict()
        return {'data': data}, 200
        

    def post(self):
        """
        print('POST')
        parser = reqparse.RequestParser()

        parser.add_argument('userId', required=True)
        parser.add_argument('name', required=True)
        parser.add_argument('city', required=True)
        print('Trying to parse')

        args = parser.parse_args()
        print('Parsed')
        """
        args = request.args
        if not args.get('userId'):
            return '', 400
        if not args.get('name'):
            return '', 400
        if not args.get('city'):
            return '', 400
        
        data = pd.read_csv('users.csv')
        
        if args.get('userId') in list(data['userId']):
            return {
                'message': f"'{args['userId']} already exists."
            }, 401
        else:
            new_data = pd.DataFrame({
            'userId': args.get('userId'),
            'name': args.get('name'),
            'city': args.get('city'),
            'locations': [[]]
            })
            data = data.append(new_data, ignore_index=True)
            data.to_csv('users.csv', index=False)
            return {'data': data.to_dict()}, 200

    def put(self):
        """
        parser = reqparse.RequestParser()
        parser.add_argument('userId', required=True)
        parser.add_argument('location', required=True)
        args = parser.parse_args()
        """
        args = request.args
        if not args.get('userId'):
            return "", 400
        if not args.get('location'):
            return "", 400

        data = pd.read_csv('users.csv')

        if args.get('userId') in list(data['userId']):
            data['locations'] = data['locations'].apply(lambda x: ast.literal_eval(x))
            user_data = data[data['userId'] == args.get('userId')]

            user_data['locations'] = user_data['locations'].values[0].append(args.get('location'))

            data.to_csv('users.csv', index=False)
            return {'data': data.to_dict()}, 200

        else:
            return {
                'message': f"'{args['userId']}' user not found."
            }, 404

    def delete(self):
        args = request.args
        if not args.get('userId'):
            return "UserID not specified", 404

        data = pd.read_csv('users.csv')
        if args.get('userId') in list(data['userId']):
            data = data[data['userId'] != args.get('userId')]
            data.to_csv('users.csv', index=False)
            return {'data': data.to_dict()}, 200
        else:
            return {
                'message': 'not found'
            }, 404

class Locations(Resource):
    pass

class Weather(Resource):
    auth_data = {'login': 'bG9naW46cGFzc3dvcmQ=', 'admin': 'YWRtaW46YWRtaW4='}

    def get(self):
        key = "945227ff-56af-4f80-8776-db001a51443b"
        args = request.args
        city = args.get('city')
        r_coord = requests.get("http://api.openweathermap.org/geo/1.0/direct?q=" + str(city) + '&limit=1&appid=62e988b73677c5c67190c729e9096c57').json()
        lat = str(r_coord[0]['lat'])
        lon = str(r_coord[0]['lon'])
        r = requests.get("https://api.weather.yandex.ru/v2/forecast?lat=" + lat + "&lon=" + lon, headers={'X-Yandex-API-Key': key}).json()
        data = r['fact']['temp']
        return {'temp': data}, 200

    def post(self):
        auth_key = request.headers.get('Authorization').split()[1]
        if auth_key in Weather.auth_data.values():
            key = "945227ff-56af-4f80-8776-db001a51443b"
            data = request.form
            city = data.get('city')
            r_coord = requests.get("http://api.openweathermap.org/geo/1.0/direct?q=" + str(city) + '&limit=1&appid=62e988b73677c5c67190c729e9096c57').json()
            lat = str(r_coord[0]['lat'])
            lon = str(r_coord[0]['lon'])
            r = requests.get("https://api.weather.yandex.ru/v2/forecast?lat=" + lat + "&lon=" + lon, headers={'X-Yandex-API-Key': key}).json()
            data = r['fact']['temp']
            return {'temp': data}, 200
        else:
            return {}, 401

        

app = Flask(__name__)
api = Api(app)

api.add_resource(Users, '/users') 
api.add_resource(Locations, '/locations')
api.add_resource(Weather, '/weather')

if __name__ == '__main__':
    app.run(debug=True, port=8000)