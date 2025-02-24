from flask import request, jsonify, g
from flask_cors import cross_origin
from datetime import datetime
import math
import sqlite3

def load(app):
  @app.route('/api/study-sessions', methods=['POST'])
  @cross_origin()
  def create_study_session():
    try:
      cursor = app.db.cursor()
      
      # Extract input data
      data = request.get_json()
      group_id = data.get('group_id')
      study_activity_id = data.get('study_activity_id')

      # Validate input data
      if group_id is None:
        return jsonify({"error": "group_id is required"}), 400
      if study_activity_id is None:
        return jsonify({"error": "study_activity_id is required"}), 400

      # Check if group_id exists
      cursor.execute('SELECT id FROM groups WHERE id = ?', (group_id,))
      if cursor.fetchone() is None:
        return jsonify({"error": "group_id does not exist"}), 400

      # Check if study_activity_id exists
      cursor.execute('SELECT id FROM study_activities WHERE id = ?', (study_activity_id,))
      if cursor.fetchone() is None:
        return jsonify({"error": "study_activity_id does not exist"}), 400

      # Insert data into the database
      cursor.execute('''
        INSERT INTO study_sessions (group_id, study_activity_id, created_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
      ''', (group_id, study_activity_id))

      # Commit the transaction
      app.db.commit()

      # Retrieve the ID of the newly created session
      session_id = cursor.lastrowid

      # Return a response
      return jsonify({"session_id": session_id}), 201

    except sqlite3.IntegrityError as e:
      return jsonify({"error": "Database integrity error: " + str(e)}), 400
    except sqlite3.DatabaseError as e:
      return jsonify({"error": "Database error: " + str(e)}), 500
    except Exception as e:
      return jsonify({"error": "An unexpected error occurred: " + str(e)}), 500

  @app.route('/api/study-sessions', methods=['GET'])
  @cross_origin()
  def get_study_sessions():
    try:
      cursor = app.db.cursor()
      
      # Get pagination parameters
      page = request.args.get('page', 1, type=int)
      per_page = request.args.get('per_page', 10, type=int)
      offset = (page - 1) * per_page

      # Get total count
      cursor.execute('''
        SELECT COUNT(*) as count 
        FROM study_sessions ss
        JOIN groups g ON g.id = ss.group_id
        JOIN study_activities sa ON sa.id = ss.study_activity_id
      ''')
      total_count = cursor.fetchone()['count']

      # Get paginated sessions
      cursor.execute('''
        SELECT 
          ss.id,
          ss.group_id,
          g.name as group_name,
          sa.id as activity_id,
          sa.name as activity_name,
          ss.created_at,
          COUNT(wri.id) as review_items_count
        FROM study_sessions ss
        JOIN groups g ON g.id = ss.group_id
        JOIN study_activities sa ON sa.id = ss.study_activity_id
        LEFT JOIN word_review_items wri ON wri.study_session_id = ss.id
        GROUP BY ss.id
        ORDER BY ss.created_at DESC
        LIMIT ? OFFSET ?
      ''', (per_page, offset))
      sessions = cursor.fetchall()

      return jsonify({
        'items': [{
          'id': session['id'],
          'group_id': session['group_id'],
          'group_name': session['group_name'],
          'activity_id': session['activity_id'],
          'activity_name': session['activity_name'],
          'start_time': session['created_at'],
          'end_time': session['created_at'],  # For now, just use the same time since we don't track end time
          'review_items_count': session['review_items_count']
        } for session in sessions],
        'total': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': math.ceil(total_count / per_page)
      })
    except Exception as e:
      return jsonify({"error": str(e)}), 500

  @app.route('/api/study-sessions/<id>', methods=['GET'])
  @cross_origin()
  def get_study_session(id):
    try:
      cursor = app.db.cursor()
      
      # Get session details
      cursor.execute('''
        SELECT 
          ss.id,
          ss.group_id,
          g.name as group_name,
          sa.id as activity_id,
          sa.name as activity_name,
          ss.created_at,
          COUNT(wri.id) as review_items_count
        FROM study_sessions ss
        JOIN groups g ON g.id = ss.group_id
        JOIN study_activities sa ON sa.id = ss.study_activity_id
        LEFT JOIN word_review_items wri ON wri.study_session_id = ss.id
        WHERE ss.id = ?
        GROUP BY ss.id
      ''', (id,))
      
      session = cursor.fetchone()
      if not session:
        return jsonify({"error": "Study session not found"}), 404

      # Get pagination parameters
      page = request.args.get('page', 1, type=int)
      per_page = request.args.get('per_page', 10, type=int)
      offset = (page - 1) * per_page

      # Get the words reviewed in this session with their review status
      cursor.execute('''
        SELECT 
          w.*,
          COALESCE(SUM(CASE WHEN wri.correct = 1 THEN 1 ELSE 0 END), 0) as session_correct_count,
          COALESCE(SUM(CASE WHEN wri.correct = 0 THEN 1 ELSE 0 END), 0) as session_wrong_count
        FROM words w
        JOIN word_review_items wri ON wri.word_id = w.id
        WHERE wri.study_session_id = ?
        GROUP BY w.id
        ORDER BY w.kanji
        LIMIT ? OFFSET ?
      ''', (id, per_page, offset))
      
      words = cursor.fetchall()

      # Get total count of words
      cursor.execute('''
        SELECT COUNT(DISTINCT w.id) as count
        FROM words w
        JOIN word_review_items wri ON wri.word_id = w.id
        WHERE wri.study_session_id = ?
      ''', (id,))
      
      total_count = cursor.fetchone()['count']

      return jsonify({
        'session': {
          'id': session['id'],
          'group_id': session['group_id'],
          'group_name': session['group_name'],
          'activity_id': session['activity_id'],
          'activity_name': session['activity_name'],
          'start_time': session['created_at'],
          'end_time': session['created_at'],  # For now, just use the same time
          'review_items_count': session['review_items_count']
        },
        'words': [{
          'id': word['id'],
          'kanji': word['kanji'],
          'romaji': word['romaji'],
          'english': word['english'],
          'correct_count': word['session_correct_count'],
          'wrong_count': word['session_wrong_count']
        } for word in words],
        'total': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': math.ceil(total_count / per_page)
      })
    except Exception as e:
      return jsonify({"error": str(e)}), 500

  @app.route('/api/study-sessions/<int:id>/review', methods=['POST'])
  @cross_origin()
  def submit_study_session_review(id):
    try:
      cursor = app.db.cursor()
      
      # Check if study session exists
      cursor.execute('SELECT id FROM study_sessions WHERE id = ?', (id,))
      if cursor.fetchone() is None:
        return jsonify({"error": "Study session not found"}), 404
      
      # Extract input data
      data = request.get_json()
      word_reviews = data.get('word_reviews', [])
      
      # Validate word_reviews structure
      if not isinstance(word_reviews, list) or not word_reviews:
        return jsonify({"error": "Word reviews must be a non-empty array"}), 400
      
      for review in word_reviews:
        # Check that each review is an object
        if not isinstance(review, dict):
          return jsonify({"error": "Each review must be an object"}), 400
        
        # Validate word_id
        word_id = review.get('word_id')
        if not isinstance(word_id, int):
          return jsonify({"error": "word_id must be a valid integer"}), 400
        
        # Validate correct
        correct = review.get('correct')
        if correct is None or not isinstance(correct, bool):
          return jsonify({"error": "correct must be a boolean value"}), 400
        
        # Check for valid word_id
        cursor.execute('SELECT id FROM words WHERE id = ?', (word_id,))
        if cursor.fetchone() is None:
          return jsonify({"error": f"word_id {word_id} does not exist"}), 400
        
        # Insert each review item into the database
        cursor.execute('''
          INSERT INTO word_review_items (word_id, study_session_id, correct)
          VALUES (?, ?, ?)
        ''', (word_id, id, correct))
      
      # Commit the transaction
      app.db.commit()
      
      return jsonify({"message": "Word reviews submitted successfully"}), 201
    
    except sqlite3.IntegrityError as e:
      return jsonify({"error": "Database integrity error: " + str(e)}), 400
    except sqlite3.DatabaseError as e:
      return jsonify({"error": "Database error: " + str(e)}), 500
    except Exception as e:
      return jsonify({"error": "An unexpected error occurred: " + str(e)}), 500

  @app.route('/api/study-sessions/reset', methods=['POST'])
  @cross_origin()
  def reset_study_sessions():
    try:
      cursor = app.db.cursor()
      
      # First delete all word review items since they have foreign key constraints
      cursor.execute('DELETE FROM word_review_items')
      
      # Then delete all study sessions
      cursor.execute('DELETE FROM study_sessions')
      
      app.db.commit()
      
      return jsonify({"message": "Study history cleared successfully"}), 200
    except Exception as e:
      return jsonify({"error": str(e)}), 500