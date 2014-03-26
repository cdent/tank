(function(){
var app = angular.module('app', []);

var POLICY_ICONS = {
	private: 'fa-lock',
	protected: 'fa-folder-o',
	public: 'fa-folder-open-o',
	custom: 'fa-wrench'
};


app.filter('escape', function() {
	return window.encodeURIComponent;
});

app.service('tankTypeIcon', function() {

	var policyMakers = {
		private: private_policy,
		protected: protected_policy,
		public: public_policy,
	};

	function private_policy(username) {
		return {
			owner: username,
			read: [username],
			write: [username],
			create: [username],
			delete: [username],
			manage: [username],
			accept: ['NONE']
		}
	}

	function protected_policy(username) {
		return {
			owner: username,
			read: [],
			write: [username],
			create: [username],
			delete: [username],
			manage: [username],
			accept: ['NONE']
		}
	}

	function public_policy(username) {
		return {
			owner: username,
			read: [],
			write: [],
			create: [],
			delete: [],
			manage: [username],
			accept: ['NONE']
		}
	}

	this.makePolicy = function(type, username) {
		return policyMakers[type](username);
	};

	this.get = function(policy) {
		var username = policy.owner;
		if (angular.equals(policy, private_policy(username))) {
			return {type: 'private', icon: POLICY_ICONS.private};
		}
		if (angular.equals(policy, protected_policy(username))) {
			return {type: 'protected', icon: POLICY_ICONS.protected};
		}
		if (angular.equals(policy, public_policy(username))) {
			return {type: 'public', icon: POLICY_ICONS.public};
		}
		return {type: 'custom', icon: POLICY_ICONS.custom};
	};
});

app.service('tankService', function($http, $q) {
	var tanks;
	this.getTanks = function() {
		if (tanks) {
			return tanks;
		}
		tanks = $http.get('/bags.json?select=policy:manage')
			.then(function(res) {
				var bags = res.data;
				var resources = bags.map(function(name) {
					var uri = '/bags/' + encodeURIComponent(name);
					return $http.get(uri,
						{headers: {'Accept': 'application/json'}});
				});
				return $q.all(resources);
			})
			.then(function(res) {
				var data = {};
				res.forEach(function(res) {
					var tankName = res.config.url
						.replace(/\/bags\/([^\/]+)/, "$1"),
						deleter = false;
					if (res.data.policy.manage.indexOf(
							res.data.policy.owner) !== -1) {
						deleter = true;
					}
					tankName = decodeURIComponent(tankName);
					angular.extend(res.data, {name: tankName,
						deleter: deleter});
					data[tankName] = res.data;
				});
				return data;
			});
		return tanks;
	};
});

app.controller('TanksCtrl', function($scope, $rootScope, $filter, $http, tankService, tankTypeIcon) {
	tankService.getTanks().then(function(data) {
		console.log('calling gettanks');
		$scope.tanks = [];
		angular.forEach(data, function(value, key) {
			angular.extend(value, tankTypeIcon.get(value.policy));
			$scope.tanks.push(value);
		});
	});

	$scope.$on('finishEdit', function(ev, data) {
		if (data) {
			var found = $filter('filter')($scope.tanks,
				{name: data.tank.name}, true);
			if (found) {
				var deleter = false;
				if (data.tank.policy.manage.indexOf(
					data.tank.policy.owner) !== -1) {
						deleter = true;
				}
				found[0].deleter = deleter;
				found[0].icon = tankTypeIcon.get(data.tank.policy).icon;
			}
		}
	});

	$scope.deleteTank = function(tank) {
		var name = tank.name,
			uri = '/bags/' + encodeURIComponent(name);
		if (confirm('Are you certain you want to delete "' + name + '"? '
					+ 'All tiddlers within will be removed!')) {
			$http.delete(uri)
				.success(function() {
					$scope.tanks = $scope.tanks.filter(function(item) {
						return item.name !== name;
					});
					$rootScope.$broadcast('deletedTank', {name: name});
				});
		}
	}
});

app.controller('TankEditor', function($scope, $http, $rootScope, tankTypeIcon) {
	$scope.constraints = ['manage', 'read', 'write', 'create', 'delete'];
	$scope.policyTypes = Object.keys(POLICY_ICONS);
	$scope.$on('startEdit', function(ev, data) {
		$scope.editTank = angular.copy(data.tank);
		$scope.originalData = angular.copy(data.tank);
		/* angular.extend($scope.editTank,
			tankTypeIcon.get($scope.editTank.policy)); */
	});

	$scope.$on('clearEdit', function() {
		$scope.editTank = null;
	});

	$scope.$on('deletedTank', function(ev, data) {
		var name = data.name;
		if ($scope.editTank && $scope.editTank.name === name) {
			$scope.editTank = null;
		}
	});

	$scope.cancelEditor = function() {
		$scope.editTank = null;
		$rootScope.$broadcast('finishEdit', {tank: $scope.originalData});
	};

	$scope.changePolicy = function(type) {
		$scope.editTank.policy = tankTypeIcon.makePolicy(type,
			$scope.editTank.policy.owner);
	};

	// XXX: move to service?
	$scope.saveTank = function() {
		var uri = '/bags/' + encodeURIComponent($scope.editTank.name);
		$http.put(uri, $scope.editTank, {headers: {'Content-Type': 'application/json'}})
			.success(function() {
				$rootScope.$broadcast('finishEdit', {
					tank: angular.copy($scope.editTank)});
				$scope.editTank = null;
			});
	};

});

app.controller('TankCtrl', function($scope, $location, $rootScope,
			tankService, tankTypeIcon)
{
	$scope.constraints = ['manage', 'read', 'write', 'create', 'delete'];

	function setData(tankName) {
		tankService.getTanks().then(function(data) {
			$scope.tanks = data;
			if ($scope.tanks[tankName]) {
				$scope.tank = angular.copy($scope.tanks[tankName]);
				angular.extend($scope.tank,
					tankTypeIcon.get($scope.tank.policy));
			}
		});
	}

	$scope.$watch(function() { return $location.path();}, 
		function(path) {
			if (path) {
				var tankName = path.split('/')[1];
				if (tankName) {
					$rootScope.$broadcast('clearEdit');
					setData(tankName);
				}
			}
		}
	);

	$scope.$on('finishEdit', function(ev, data) {
		if (data) {
			$scope.tank = angular.copy(data.tank);
			$scope.tanks[$scope.tank.name] = $scope.tank;
			angular.extend($scope.tank, tankTypeIcon.get($scope.tank.policy));
		}
	});

	$scope.$on('deletedTank', function(ev, data) {
		var name = data.name;
		if ($scope.tank && $scope.tank.name === name) {
			$scope.tank = null;
		}
	});

	$scope.startEditor = function() {
		$rootScope.$broadcast('startEdit', {tank: $scope.tank});
		$scope.tank = null;
	};

});
})();
