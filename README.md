## Get started

1. Run docker compose

   ```bash
   docker compose up --build
   ```

2. Run pull-models.sh
   ```bash
   ./pull-models.sh
   ```
3. Configure environment variables

   Create a `.env` file in the backend directory of the project with the following content:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. Run the front end

   ```bash
   cd frontend
   npm install
   npm run web
   ```

5. Open the browser, and go to http://localhost:8081

# Approaches

Due to the data dependency chain, For example, to get someone's order detail, we will need

1. Get the customer data, including the customer id
2. Use the customer id get all of the related inventory data including the inventory id
3. Use the inventory id get all of the related order detail data including the order id
4. Use the order id get the order detail

## My initial approach

AI agent architecture, define two agent,

1. main agent will understand the relationship between the datas, and can handoff to the data agent to retrive the corresponding data, and the depended data needed, and answer the question based on the data retrived
2. data agent will retrive the data using file retrivel tool call, to get the data from the file

Pro:

1. Adaptable, since agent can understand the relationship between the datas, and retrive the corresponding data
2. Easy to horizontal scale(for small amount), we can simply add the relationship into the main agent prompt, and more tool calls to the data agent
3. Easy to vertical scale, since the data agent retrive the data through function call, retrive the data just simply read the file and return the data

Con:

1. Relationship between the datas must be clearly described in the main agent prompt. If there the relationship get more
   complex, or huge horizontal scale, it will be hard to maintain and debug
2. Reliability, since the main agent determine the type of data needed to answer the question, it can be unreliable if the agent missed some part of the data

## My final approach

AI Agent Architecture + RAG + Rule based

If the relationship between the datas must be clearly described, and still can lose realiablity,

### Then why not just use the rule based approach?

Is just whether you tell agent the rule, or you code based on the rule
And clearly code based on the rule can be much faster and more reliable

### Define the agent, and

1.  if user is asking data from a particular file,
    then use the tool call that will retrive the data from a vector store and
    generate the answer based on the data retrived
2.  If user is asking data about someone's order, and since the order date is depend on another file(eg. inventory id, customer id),
    then use the tool call that will get the customer id, and use the customer id to get all of the inventory data related, and then use the inventory id to get all of the order data related, and then use the order date to get the order detail, and use the item_id get all of the price data, and then generate the answer based on the data retrived

### Because RAG and rule based approach used together, horizontal scale(extend the rule)and vertical scale(vector store used), and relaibility(RAG, rule based infor retrival) are ensured
