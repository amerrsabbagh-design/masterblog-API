from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort = request.args.get('sort')
    direction = request.args.get('direction')
    if not sort and not direction:
        return jsonify(POSTS), 200
    if sort not in ('title', 'content'):
        return jsonify({
            "error": "Invalid sort field. Use 'title' or 'content'."
        }), 400
    if direction not in ('asc', 'desc'):
        return jsonify({
            "error": "Invalid direction. Use 'asc' or 'desc'."
        }), 400
    reverse = (direction == 'desc')
    sorted_posts = sorted(
        POSTS,
        key=lambda post: post[sort].lower(),
        reverse=reverse
    )
    return jsonify(sorted_posts), 200


@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    missing = []
    if 'title' not in data or not data['title']:
        missing.append('title')
    if 'content' not in data or not data['content']:
        missing.append('content')
    if missing:
        return jsonify({
            "error": "Missing required fields",
            "missing": missing
        }), 400
    if POSTS:
        new_id = max(post["id"] for post in POSTS) + 1
    else:
        new_id = 1

    new_post = {
        "id": new_id,
        "title": data["title"],
        "content": data["content"]
    }

    POSTS.append(new_post)

    return jsonify(new_post), 201

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    for index, post in enumerate(POSTS):
        if post["id"] == post_id:
            POSTS.pop(index)
            return jsonify({
                "message": f"Post with id {post_id} has been deleted successfully."
            }), 200

    return jsonify({
        "error": f"Post with id {post_id} was not found."
    }), 404

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.get_json() or {}
    for post in POSTS:
        if post["id"] == post_id:
            if "title" in data and data["title"] is not None:
                post["title"] = data["title"]
            if "content" in data and data["content"] is not None:
                post["content"] = data["content"]
            return jsonify(post), 200
    return jsonify({
        "error": f"Post with id {post_id} was not found."
    }), 404

@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title_query = request.args.get('title', '', type=str).lower()
    content_query = request.args.get('content', '', type=str).lower()
    if not title_query and not content_query:
        return jsonify(POSTS), 200

    results = []
    for post in POSTS:
        title = post["title"].lower()
        content = post["content"].lower()

        match_title = title_query in title if title_query else False
        match_content = content_query in content if content_query else False

        if match_title or match_content:
            results.append(post)

    return jsonify(results), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
