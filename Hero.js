import * as THREE from 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.module.js';

export class Hero {
    constructor(scene, color = 0x00ff00) {
        this.group = new THREE.Group();
        
        // ТЕЛО (Броня)
        const bodyGeo = new THREE.CapsuleGeometry(0.5, 1, 4, 8);
        const bodyMat = new THREE.MeshStandardMaterial({ color: color });
        this.body = new THREE.Mesh(bodyGeo, bodyMat);
        this.body.position.y = 1;
        this.group.add(this.body);

        // ГОЛОВА
        const headGeo = new THREE.BoxGeometry(0.5, 0.5, 0.5);
        const headMat = new THREE.MeshStandardMaterial({ color: 0xffdbac }); // Цвет кожи
        this.head = new THREE.Mesh(headGeo, headMat);
        this.head.position.y = 1.8;
        this.group.add(this.head);

        // РУКИ (Плечи)
        const armGeo = new THREE.BoxGeometry(0.3, 0.7, 0.3);
        const lArm = new THREE.Mesh(armGeo, bodyMat);
        lArm.position.set(0.6, 1.2, 0);
        const rArm = new THREE.Mesh(armGeo, bodyMat);
        rArm.position.set(-0.6, 1.2, 0);
        this.group.add(lArm, rArm);

        scene.add(this.group);
        
        this.speed = 0.08;
        this.radius = 0.6; // Радиус для коллизий
    }

    update(moveX, moveZ, obstacles) {
        if (Math.abs(moveX) < 0.01 && Math.abs(moveZ) < 0.01) return;

        // Рассчитываем новую потенциальную позицию
        let nextX = this.group.position.x + moveX * this.speed;
        let nextZ = this.group.position.z + moveZ * this.speed;

        // ПРОВЕРКА КОЛЛИЗИЙ
        let canMoveX = true;
        let canMoveZ = true;

        for (let obs of obstacles) {
            // Упрощенная проверка коллизий (AABB или дистанция)
            // Здесь используем проверку по дистанции до центра препятствия
            const obsPos = obs.position;
            const dx = nextX - obsPos.x;
            const dz = this.group.position.z - obsPos.y; // Для оси X проверяем текущий Z
            
            // Если препятствие — башня (цилиндр) или куст (куб)
            // Берем примерный размер препятствия 2.5 единицы
            const minDist = this.radius + 2.0; 

            // Проверка по X
            if (Math.sqrt((nextX - obs.position.x)**2 + (this.group.position.z - obs.position.z)**2) < minDist) {
                canMoveX = false;
            }
            // Проверка по Z
            if (Math.sqrt((this.group.position.x - obs.position.x)**2 + (nextZ - obs.position.z)**2) < minDist) {
                canMoveZ = false;
            }
        }

        if (canMoveX) this.group.position.x = nextX;
        if (canMoveZ) this.group.position.z = nextZ;

        // Поворот персонажа в сторону движения
        const angle = Math.atan2(moveX, moveZ);
        this.group.rotation.y = angle;
    }
                                                                         }
