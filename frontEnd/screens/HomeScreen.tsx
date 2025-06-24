import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Platform } from 'react-native';
import { useNavigation, NavigationProp } from '@react-navigation/native';

type RootStackParamList = {
  Home: undefined;
  DirectSearch: undefined;
  NearestParking: undefined;
};

export function HomeScreen() {
  const navigation = useNavigation<NavigationProp<RootStackParamList>>();
  
  return (
    <View style={styles.homeContainer}>
      <View style={styles.gradientOverlay}>
        <Text style={styles.pageTitle}>Parking Spotter</Text>
        <TouchableOpacity 
          style={[styles.card, styles.cardPrimary]}
          onPress={() => navigation.navigate('DirectSearch')}
          activeOpacity={0.8}
        >
          <View style={styles.cardContent}>
            <Text style={styles.cardIcon}>🔍</Text>
            <Text style={styles.cardTitle}>Search Cameras</Text>
            <Text style={styles.cardDescription}>
              Search specific parking camera locations by address
            </Text>
          </View>
          <View style={styles.cardGlow} />
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.card, styles.cardSecondary]}
          onPress={() => navigation.navigate('NearestParking')}
          activeOpacity={0.8}
        >
          <View style={styles.cardContent}>
            <Text style={styles.cardIcon}>📍</Text>
            <Text style={styles.cardTitle}>Find Nearest Parking</Text>
            <Text style={styles.cardDescription}>
              Locate street cameras near your current location
            </Text>
          </View>
          <View style={styles.cardGlow} />
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  homeContainer: {
    flex: 1,
    backgroundColor: '#0f001a',
  },
  gradientOverlay: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
    backgroundColor: 'rgba(46, 0, 62, 0.8)',
  },
  pageTitle: {
    color: '#FFB366',
    fontSize: 36,
    fontWeight: '900',
    fontFamily: Platform.OS === 'ios' ? 'Courier New' : 'monospace',
    textAlign: 'center',
    marginBottom: 40,
    textShadowColor: '#8B5FBF',
    textShadowOffset: { width: -2, height: 3 },
    textShadowRadius: 8,
    letterSpacing: 4,
    textTransform: 'uppercase',
    transform: [{ skewX: '-5deg' }],
  },
  card: {
    borderRadius: 20,
    padding: 28,
    marginBottom: 24,
    position: 'relative',
    overflow: 'hidden',
    elevation: 12,
    shadowColor: '#FF8C42',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.5,
    shadowRadius: 15,
  },
  cardPrimary: {
    backgroundColor: '#2a0040',
    borderWidth: 2,
    borderColor: 'rgba(255, 140, 66, 0.4)',
  },
  cardSecondary: {
    backgroundColor: '#1a002b',
    borderWidth: 2,
    borderColor: 'rgba(255, 140, 66, 0.4)',
  },
  cardContent: {
    alignItems: 'center',
    zIndex: 2,
  },
  cardGlow: {
    position: 'absolute',
    top: -50,
    right: -50,
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: 'rgba(255, 140, 66, 0.2)',
    zIndex: 1,
  },
  cardIcon: {
    fontSize: 48,
    marginBottom: 12,
    textShadowColor: 'rgba(255, 140, 66, 0.6)',
    textShadowOffset: { width: 0, height: 3 },
    textShadowRadius: 6,
  },
  cardTitle: {
    color: '#FFB366',
    fontSize: 24,
    fontWeight: '900',
    fontFamily: Platform.OS === 'ios' ? 'Courier New' : 'monospace',
    marginBottom: 12,
    textAlign: 'center',
    textShadowColor: '#8B5FBF',
    textShadowOffset: { width: -1, height: 2 },
    textShadowRadius: 6,
    letterSpacing: 2,
    textTransform: 'uppercase',
    transform: [{ skewX: '-3deg' }],
  },
  cardDescription: {
    color: '#e0b3ff',
    fontSize: 14,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    textAlign: 'center',
    lineHeight: 20,
    opacity: 0.9,
    paddingHorizontal: 4,
    letterSpacing: 0.5,
    fontWeight: '600',
  },
}); 