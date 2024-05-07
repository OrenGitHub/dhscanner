FROM node
WORKDIR /usr/app
RUN npm install express
RUN npm install vm2
COPY main.js main.js
EXPOSE 3000
CMD ["node", "main.js"]